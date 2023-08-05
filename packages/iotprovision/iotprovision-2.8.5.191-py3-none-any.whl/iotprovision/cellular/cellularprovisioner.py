"""
Cellular provisioning classes
"""

import hashlib
import binascii
from time import sleep
import boto3
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from pyawsutils.mar import aws_mar
from pyawsutils.aws_cloudformation import MCHP_SANDBOX_ATS_ENDPOINT
from pyawsutils.aws_ca_cert import aws_get_root_ca_cert_filename
from pytrustplatform.ecc_cert_builder import build_certs_from_ecc
from pytrustplatform.device_cert_builder import build_device_cert

from ..provisioner import Provisioner, ProvisionerAwsMar, ProvisionerAwsJitr, ProvisionerError
from ..config import Config
from ..kit_config import kit_configure_disk_link
from ..eccstorage import EccStorage
from .atprovisioner import AtProvisioner
from .sequans_ciphersuites import print_ciphersuites, validate_ciphersuites, DEFAULT_CIPHERSUITES

DEFAULT_CELLULAR_PROVIDER = "standard"

# list of valid frequency band values.
CELLULAR_VALID_FREQ_BANDS = [1, 2, 3, 4, 5, 8, 12, 13, 14, 17, 18, 19, 20, 25, 26, 28, 66, 71, 85]

def get_cellular_provisioner(programmer, args):
    """
    Resolves the cellular provisioning algorithm requested by the user
    """
    if args.cloud_provider == "google":
        # Only one option for Google
        return CellularProvisionerGoogle(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider == "aws":
        # AWS can be done many ways:
        if args.provision_method == "mar":
            # Multi-Account registration (to user account)
            return CellularProvisionerAwsMar(programmer, args.skip_program_provision_firmware, args.port)
        if args.provision_method == "jitr":
            # Just-In-Time Registration (to user account)
            return CellularProvisionerAwsJitr(programmer, args.skip_program_provision_firmware, args.port)
        # Microchip sandbox
        return CellularProvisionerAws(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider == "azure":
        # Azure (preliminary)
        return CellularProvisionerAzure(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider is None:
        # This choice is valid for debuggerupgrade action
        return CellularProvisioner(programmer, args.skip_program_provision_firmware, args.port)

    raise ProvisionerError("Unable find Cellular provisioner for {} - {}".format(args.cloud_provider,
                                                                                 args.provision_method))


class CellularProvisioner(Provisioner):
    """
    This class implements provisioning for AVR-IoT Cellular kit. Its subclasses mirrors the structure of the
    Provisioner class hierarchy.
    """

    DEVICE_CERT_SLOT = 0
    DEVICE_PRIVATEKEY_SLOT = 0
    ROOT_CERT_SLOT = 19

    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        super().__init__(programmer, skip_program_provision_fw, port=port)
        self.provider = DEFAULT_CELLULAR_PROVIDER
        self.frequency_bands = None  # None means don't configure frequency bands for provider.
        self.aws_profile = None
        self.ciphersuites = None
        self.client_key_storage = 1  # Use ECC private key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()

    def set_cellular_params(self, args):
        """
        Set up Cellular specific parameters that cannot be passed in constructor due to protocol

        :param args: Parsed-out command-line arguments
        """
        self.provider = None                     # => Don't change provider
        self.frequency_bands = None              # => Don't change bands. FIXME: move to pysequans?
        self.ciphersuites = validate_ciphersuites(DEFAULT_CIPHERSUITES.get(args.cloud_provider, []))
        self.aws_profile = args.aws_profile

    def connect(self, function, skip_programming=False):
        """
        Implement additional steps to synchronize with Sequans modem reset after initial FW programming/reset

        :param function: Firmware function (eg. "iotprovision") as defined
        :param skip_programming: Skip programming FW.
        """
        super().connect(function, skip_programming)
        # At this point we should be freshly out of reset and in sync with the firmware, we now should synchronize
        # with Sequans modem, eg by means of waiting for +SYSSTART URC in bridge mode.
        # FIXME: However could not make that work, so just do a mystery delay for now.
        # The minimum delay required is surprisingly consistent 0.9-1.0 seconds
        sleep(1.2)

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Common part of Cellular provisioning, independent of cloud provider and method. Subclasses should
        override this and append their specific parts of provisioning.

        :param force_new_device_certificate: Force creation of device certificates
        :param skip_program_provision_firmware: Skip programming provisioning FW. Compatible FW
            must be programmed previously, this is user's responsibility
        """
        self.connect("iotprovision", skip_programming=skip_program_provision_firmware)

        # Set up basic connection parameters in modem, common for all cloud providers
        self.logger.info("Setting up modem")
        with AtProvisioner(self.fwinterface) as atprovisioner:
            atprovisioner.set_provider(self.provider)
            if self.frequency_bands:
                atprovisioner.set_frequency_bands(self.provider, self.frequency_bands)

    @staticmethod
    def validate_int_list(values, valids, base=10):
        """
        Validate list of integer values and convert to integer list.
        It is assumed all integers in list are in same base.

        :param values: String with comma-separated integers
        :param valids: List of valid integer values
        :param base: Base expected in input
        :return: List of strings representing values in selected base. Modem expects a
            specific base in list as a string, depending on command,
            and all values must be in same base (decimal, hex, ...)
        :raise: ValueError if invalid values specified
        """
        if values is None:
            return None
        if not values:
            return ""
        valid = []
        invalid = []
        for value in values.split(","):
            try:
                if int(value, base=base) in valids:
                    valid.append(value)
                else:
                    invalid.append(value)
            except ValueError:
                invalid.append(value)
        if invalid:
            raise ValueError(f"Invalid value(s): {','.join(invalid)}")
        return valid

    @staticmethod
    def create_cert_chain(certfiles, outfile=None):
        """
        Create a certificate chain, basically a concatenation of PEM files.

        :param certfiles: List of input certificate file names in PEM format.
        :param outfile: Optional output file name for saving chain
        :return: Certificate chain
        """
        chain = b""
        for file in certfiles:
            with open(file, "rb") as f:
                chain += f.read()
                # Make sure cert ends with a newline
                if not chain.endswith(b"\n"):
                    s += b"\n"
        if outfile:
            with open(outfile, "w") as f:
                f.write(chain)
        return chain


class CellularProvisionerAzure(CellularProvisioner):
    """
    Azure provisioning mechanisms for Cellular
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        super().__init__(programmer, skip_program_provision_fw, port=port)
        self.cloud_provider = "azure"
        raise NotImplementedError("'{}' not yet implemented".format(type(self).__name__))


class CellularProvisionerGoogle(CellularProvisioner):
    """
    Google provisioning mechanism for Cellular
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        super().__init__(programmer, skip_program_provision_fw, port=port)
        self.cloud_provider = "google"
        raise NotImplementedError("'{}' not yet implemented".format(type(self).__name__))


class CellularProvisionerAws(CellularProvisioner):
    """
    AWS Microchip Sandbox provisioning mechanism for Cellular
    """

    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        super().__init__(programmer, skip_program_provision_fw, port=port)
        self.cloud_provider = "aws"

    #pylint: disable=unused-argument
    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        """
        Generate CA certificates
        Nothing to do for AWS Sandbox
        """
        return

    def create_device_certs_ecc(self, device_cert_file, signer_cert_file, force=False):
        """
        Create device and signer certificate from ECC, if not already existing

        :param device_cert_file: Device certificate filename
        :param signer_cert_file: Signer certificate filename
        :return: Thing name extracted from certificate
        """
        self.logger.info("Generating device certificates")
        device_cert, _ = build_certs_from_ecc(self.fwinterface.get_firmware_driver(),
                                              signer_cert_file, device_cert_file,
                                              force=force)
        try:
            # FIXME: Why is this thing name extraction different from custom provisioning?
            ski = device_cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_KEY_IDENTIFIER).value.digest
            thing_name = binascii.b2a_hex(ski).decode()
        except x509.ExtensionNotFound:
            pubkey = device_cert.public_key().public_bytes(encoding=serialization.Encoding.DER,
                                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
            thing_name = hashlib.sha1(pubkey[-65:]).hexdigest()
        return thing_name

    def store_provisioning_data(self, thingname, endpoint, device_cert_file, root_ca_cert_file):
        """
        Save provisioning data to kit.

        :param thingname: AWS thing name
        :param endpoint: AWS endpoint
        :param device_cert: Device certificate in PEM format
        :param root_ca_cert: Root CA certificate, PEM format
        """
        aws_thing_file = Config.Certs.get_path("aws_thing_file", self.serialnumber)
        self.store_iot_id(thingname, aws_thing_file)

        self.logger.info("Writing to ECC slot 8:\n"
                         "  Thing name: %s\n"
                         "  Endpoint:   %s", thingname, endpoint)
        self.fwinterface.eccstorage.create_write_provinfo([
            (EccStorage.AWS_THINGNAME, thingname),
            (EccStorage.AWS_ENDPOINT, endpoint)])

        # FIXME: Read back and verify. Remove this when we trust EccStorage entirely
        self.logger.debug("Verify correct ECC write")
        data = self.fwinterface.eccstorage.read_provinfo()
        assert len(data) == 2
        assert data[0] == (EccStorage.AWS_THINGNAME, thingname.encode())
        assert data[1] == (EccStorage.AWS_ENDPOINT, endpoint.encode())

        with open(root_ca_cert_file, "rb") as f:
            root_ca_cert = f.read()

        with open(device_cert_file, "rb") as f:
            device_cert = f.read()

        self.logger.info("Writing certificates to modem")
        with AtProvisioner(self.fwinterface) as atprovisioner:
            atprovisioner.write_slot("certificate", device_cert, self.DEVICE_CERT_SLOT)
            atprovisioner.write_slot("certificate", root_ca_cert, self.ROOT_CERT_SLOT)
            atprovisioner.set_security_profile(server_ca=self.ROOT_CERT_SLOT,
                                               client_cert=self.DEVICE_CERT_SLOT,
                                               ciphersuites=self.ciphersuites,
                                               client_key_storage=self.client_key_storage)


    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Sandbox provisioning for AWS
        """
        super().do_provision(force_new_device_certificate, skip_program_provision_firmware)

        device_cert_file = Config.Certs.get_path("device_cert_file_sandbox", self.serialnumber)
        signer_cert_file = Config.Certs.get_path("signer_cert_file_sandbox", self.serialnumber)

        thingname = self.create_device_certs_ecc(device_cert_file, signer_cert_file, force=force_new_device_certificate)

        self.store_provisioning_data(thingname, MCHP_SANDBOX_ATS_ENDPOINT, device_cert_file,
                                     aws_get_root_ca_cert_filename("aws_ca_bundle"))

        self.disconnect()

        # Change the disk link after provisioning
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider=self.cloud_provider,
                                key2_value=thingname)
        self.debugger_reboot_required = True

    def get_aws_endpoint(self):
        """
        Get AWS endpoint when custom provisioning is used
        """
        # FIXME: This should be in pyawsutils!
        aws_session = boto3.session.Session(profile_name=self.aws_profile)
        aws_iot = aws_session.client("iot")
        return aws_iot.describe_endpoint(endpointType="iot:Data-ATS").get("endpointAddress")


class CellularProvisionerAwsMar(ProvisionerAwsMar, CellularProvisionerAws):
    """
    AWS MAR provisioning mechanism for Cellular
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        CellularProvisionerAws.__init__(self, programmer, skip_program_provision_fw, port=port)

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Provisioning for AWS MAR
        """
        #FIXME: This is almost the same as sandbox provisioning, consider common method with parameters
        # (endpoint, disklink) if things don't change-
        CellularProvisioner.do_provision(self, force_new_device_certificate, skip_program_provision_firmware)

        device_cert_file = Config.Certs.get_path("device_cert_file", self.serialnumber)
        signer_cert_file = Config.Certs.get_path("signer_cert_file", self.serialnumber)

        thingname = self.create_device_certs_ecc(device_cert_file, signer_cert_file, force=force_new_device_certificate)

        # Register device certificate without CA for custom provisioning with MAR
        aws_mar_tool = aws_mar(aws_profile=self.aws_profile_name)
        aws_mar_tool.create_device(certificate_file=device_cert_file,
                                   policy_name="zt_policy", thing_type=None)

        self.store_provisioning_data(thingname, self.get_aws_endpoint(), device_cert_file,
                                     aws_get_root_ca_cert_filename("aws_ca_bundle"))

        self.disconnect()

        # Change the disk link after reprovisioning
        # Note: disk link will not lead to data in the user's custom account.
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider='awscustom',
                                key2_value=thingname)
        self.debugger_reboot_required = True


class CellularProvisionerAwsJitr(ProvisionerAwsJitr, CellularProvisionerAws):
    """
    AWS JITR provisioning mechanism for Cellular
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None):
        CellularProvisionerAws.__init__(self, programmer, skip_program_provision_fw, port=port)

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Provisioning for AWS JITR
        """
        CellularProvisioner.do_provision(self, force_new_device_certificate, skip_program_provision_firmware)

        self.logger.info("Generating device certificate")
        device_cert = build_device_cert(self.fwinterface.get_firmware_driver(),
                                        Config.Certs.get_path("signer_ca_cert_file"),
                                        Config.Certs.get_path("signer_ca_key_file"),
                                        Config.Certs.get_path("device_csr_file", self.serialnumber),
                                        Config.Certs.get_path("device_cert_file", self.serialnumber),
                                        force=force_new_device_certificate)

        thingname = None
        for extension in device_cert.extensions:
            if extension.oid._name != 'subjectKeyIdentifier':
                continue # Not the extension we're looking for, skip
            thingname = binascii.b2a_hex(extension.value.digest).decode('ascii')

        self.store_provisioning_data(thingname, self.get_aws_endpoint(),
                                     Config.Certs.get_path("device_cert_file", self.serialnumber),
                                     aws_get_root_ca_cert_filename("aws_ca_bundle"))

        self.disconnect()

        # Change the disk link after reprovisioning
        # Note: disk link will not lead to data in the user's custom account.
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider='awscustom',
                                key2_value=thingname)
        self.debugger_reboot_required = True
