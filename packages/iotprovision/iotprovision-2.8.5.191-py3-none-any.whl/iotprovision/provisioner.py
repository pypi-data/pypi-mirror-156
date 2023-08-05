"""
Provisioner class, implement API for provisioning.
"""
import os
import time
from logging import getLogger
from packaging import version
from packaging.version import parse as version_parse

from pydebuggerupgrade.backend import Backend

from pyawsutils.mar import aws_mar
from pyawsutils.register_signer import register_signer
from pyawsutils.aws_cloudformation import setup_aws_jitr_account
from pyawsutils.policy import create_policy_mar

from pytrustplatform.ca_create import ca_create_root
from pytrustplatform.ca_create import ca_create_signer_csr
from pytrustplatform.ca_create import ca_create_signer
from pytrustplatform.ca_create import DEFAULT_ORGANIZATION_NAME, DEFAULT_ROOT_COMMON_NAME, DEFAULT_SIGNER_COMMON_NAME

from pykitcommander.kitprotocols import setup_kit

from .config import Config
from .kit_config import kit_configure_disk_link
from .version import VERSION
from .winc.wincupgrade import WincUpgrade
from .winc.winc_flash_map import FlashMap

from .firmwareinterface import ProvisioningFirmwareInterface, WincUpgradeFirmwareInterface, DemoFirmwareInterface

from .aws.sandbox_provision import AwsSandboxProvisioner
from .aws.custom_provision import AwsCustomProvisioner
from .azure.custom_provision import AzureCustomProvisioner

# Map strings to values according to enum tenumM2mSecType
# in winc/driver/include/m2m_types.h
WIFI_AUTHS = {"open": "1", "wpa-psk": "2", "wep": "3", "ieee802.1x": "4"}

class ProvisionerError(Exception):
    """
    Provisioner specific exception
    """
    def __init__(self, msg=None):
        super().__init__(msg)


def get_provisioner(programmer, args):
    """
    Resolves the provisioning algorithm requested by the user
    """
    if args.cloud_provider == "google":
        # Only one option for Google
        return ProvisionerGoogle(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider == "aws":
        # AWS can be done many ways:
        if args.provision_method == "mar":
            # Multi-Account registration (to user account)
            return ProvisionerAwsMar(programmer, args.skip_program_provision_firmware, args.port)
        if args.provision_method == "jitr":
            # Just-In-Time Registration (to user account)
            return ProvisionerAwsJitr(programmer, args.skip_program_provision_firmware, args.port)
        # Microchip sandbox
        return ProvisionerAws(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider == "azure":
        # Azure (preliminary)
        return ProvisionerAzure(programmer, args.skip_program_provision_firmware, args.port)
    if args.cloud_provider is None:
        # This choice is valid for debuggerupgrade, wincupgrade actions
        return Provisioner(programmer, args.skip_program_provision_firmware, args.port)

    raise ProvisionerError("Unable find provisioner for {} - {}".format(args.cloud_provider, args.provision_method))

class Provisioner():
    """
    IOT provisioner API base class
    This class provides functions which the provisioning algorithm (caller) can use to perform its tasks.
    The base class provides only generic functionality. Where provider-specific implementation is required,
    a sub-class can be used.

    Hierarchy:

    .. code-block:: text

        Provisioner
        |
        |- ProvisionerGoogle
        |- ProvisionerAzure
        |- ProvisionerAws
            |
            |- ProvisionerAwsMar
            |- ProvisionerAwsJitr

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    # Map supported pykitcommander protocol_class identifiers to internal implementations
    FW_INTERFACES = {
        "ProvisioningV2": ProvisioningFirmwareInterface,
        "WxDemoV1": DemoFirmwareInterface,
        "WincUpgradeV1": WincUpgradeFirmwareInterface
        }

    # Absolute minimum debugger version required for provisioning to work
    MINIMUM_DEBUGGER_VERSION = "1.15.479"

    def __init__(self, programmer, skip_program_provision_fw=False, port=None,
                 installdir=os.path.abspath(os.path.dirname(__file__))):
        """
        Constructor requires a single kit being identified, use last digits
        of serial number to disambiguate.
        """
        self.logger = getLogger(__name__)
        self.programmer = programmer
        self.port = programmer.kit_info.get("serial_port")
        if port:
            if self.port:
                self.logger.warning("Serial port '%s' auto-detected, ignoring request for port '%s'", self.port, port)
            else:
                # User provided port name only if not provided from pykitcommander
                self.port = port
        self.logger.debug("Using serial port '%s'", self.port)
        self.skip_program_provision_fw = skip_program_provision_fw
        self.version = version.Version(VERSION)
        self.installdir = installdir
        self.serialnumber = self.programmer.kit_info["serialnumber"]
        self.profile_name = None
        self.kit_info = None
        self.fwinterface = None
        self.aws_profile_name = None
        self.debugger_reboot_required = False

    def __del__(self):
        self.disconnect()

    def configure_kit(self, function, skip_programming=False):
        """
        Configure kit for provisioning function, program FW if required

        :param function: Firmware function (eg. "iotprovision") as defined
        :type function: str
        :param skip_programming: Skip programming FW. Use with extreme care!
        :type skip_programming: boolean
        """
        if self.fwinterface:
            self.disconnect()
        self.logger.debug("Setup request to pykitcommander for application: '%s'", function)
        try:
            self.kit_info = setup_kit(function, skip_programming=skip_programming,
                                      programmer=self.programmer)
        except Exception as e:
            self.logger.debug("Pykitcommander Setup application '%s' failed with %s: %s", function, type(e).__name__, e)
            raise e

    def connect(self, function, skip_programming=False):
        """
        Connect actively to the kit for provisioning function, program FW if required

        :param function: Firmware function (eg. "iotprovision") as defined
        :type function: str
        :param skip_programming: Skip programming FW. Use with extreme care!
        :type skip_programming: boolean
        """
        self.configure_kit(function=function, skip_programming=skip_programming)

        protocol_id = self.kit_info.get("protocol_id")

        # If protocol is not defined, skip connect
        if not protocol_id:
            self.logger.error("Protocol for '%s' is not defined and cannot be used.", function)
            return

        fwinterface = self.FW_INTERFACES.get(protocol_id)
        if not fwinterface:
            raise ProvisionerError(f"Firmware protocol '{protocol_id}' not supported")
        self.fwinterface = fwinterface(self.kit_info, self.programmer, port=self.port)
        self.fwinterface.open()

        # Get firmware version, sanity check and print for information
        # TODO: Check that we have required version.
        version = self.fwinterface.read_fw_version()
        if version:
            self.logger.info("Firmware '%s' version: %s", function, version)
        else:
            raise ProvisionerError(f"Could not read '{function}' firmware version")

    def disconnect(self):
        if self.fwinterface:
            self.fwinterface.close()
        self.fwinterface = None

    #pylint: disable=unused-argument
    def setup_account(self, profile_name, force_setup):
        self.logger.info("No account setup required")

    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        self.logger.info("No certificate generation required for this provider")

    @staticmethod
    def create_root_of_trust(force=False, org_name=DEFAULT_ORGANIZATION_NAME,
                             root_common_name=DEFAULT_ROOT_COMMON_NAME,
                             signer_common_name=DEFAULT_SIGNER_COMMON_NAME):
        """
        Create certificates.

        :param force: Set to True to force regeneration
        :type force: boolean
        :param org_name: Organization name
        :type org_name: str
        :param root_common_name: Common name of Root
        :type root_common_name: str
        :param signer_common_name: Common name of Signer
        :type signer_common_name: str
        """
        ca_create_root(force=force, root_ca_key_path=Config.Certs.get_path("root_ca_key_file"),
                       root_ca_cert_path=Config.Certs.get_path("root_ca_cert_file"),
                       org_name=org_name, common_name=root_common_name)

        ca_create_signer_csr(force=force, signer_ca_key_path=Config.Certs.get_path("signer_ca_key_file"),
                             signer_ca_csr_path=Config.Certs.get_path("signer_ca_csr_file"),
                             org_name=org_name, common_name=signer_common_name)

        ca_create_signer(force=force, signer_ca_csr_path=Config.Certs.get_path("signer_ca_csr_file"),
                         signer_ca_cert_path=Config.Certs.get_path("signer_ca_cert_file"),
                         root_ca_key_path=Config.Certs.get_path("root_ca_key_file"),
                         root_ca_cert_path=Config.Certs.get_path("root_ca_cert_file"))

    @staticmethod
    def store_iot_id(iot_id, iot_id_filename):
        """
        Store the identifier of a device

        Identifier will be available from file if kit has previously been provisioned on this computer.
        This identifier is the unique identifier of a node/device in IoT.
        Terminology varies among cloud providers, e.g. Thing Name for AWS or Device ID for Azure.

        :param iot_id: ID
        :type iot_id: str
        :param iot_id_filename: File to store ID in
        :type iot_id_filename: str
        """
        if iot_id:
            with open(iot_id_filename, "w") as idfile:
                idfile.write(iot_id)

    def erase_target_device(self):
        """
        Erases the target device as clean-up step
        """
        self.logger.info("Erasing target device")
        self.disconnect()
        self.programmer.erase()

    def reboot_debugger(self):
        """
        Reboot debugger to invalidate USB mass storage cache for click-me file change.
        This tends to upset subsequent programming operations in some circumstances,
        so do it last in provisioning session
        """
        self.programmer.reboot()

    def get_debugger_version(self):
        """
        Get debugger version installed on selected kit.
        """
        backend = Backend()
        return backend.get_current_version("nedbg", self.serialnumber)

    def debuggerupgrade(self, tool):
        """
        Update kit's debugger firmware to bundled file

        :param tool: tool to upgrade
        :type tool: str
        """
        backend = Backend()
        # Upgrade with bundled zip
        nedbg_fw = os.path.join(self.installdir, "fw", "nedbg_fw.zip")

        upgraded, installed_version = backend.upgrade_from_source(source=nedbg_fw, tool_name=tool,
                                                                  serialnumber=self.serialnumber)
        if upgraded:
            self.logger.info("Upgraded debugger firmware to version %s", installed_version)
            # When debugger has been upgraded it will require some time to reboot and become available on the USB bus
            self.logger.debug("Wait for debugger to become available after upgrade...")
            retries = 5
            while retries:
                matching = backend.get_matching_tools(tool_name=tool, serialnumber_substring=self.serialnumber)
                if matching:
                    # The unit is back on the bus, nothing more needs to be done, any existing connections will
                    # continue to work
                    return
                retries -= 1
                if retries:
                    self.logger.debug("Debugger not available yet, polling again in a second...")
                    # Wait a bit before retrying
                    time.sleep(1)
                else:
                    self.logger.error("Timed out waiting for debugger to become available after upgrade")
                    # Just let execution continue. An exception will be raised on next attempt to connect to the
                    # debugger
        else:
            self.logger.info("Debugger firmware already up to date (%s)", installed_version)

    def program_application(self, cloud_provider):
        """
        Program demo application for selected cloud provider

        :param cloud_provider: Cloud provider in use
        :type cloud_provider: str
        """
        function = "demo-{}".format(cloud_provider)
        # Just program application, no connection
        self.configure_kit(function)
        app_info = self.kit_info.get("application_info")
        fw_version = app_info.get("bundled_firmware_version", "Unknpown") if app_info else "Unknown"
        self.logger.info("Firmware '%s' version: %s", function, fw_version)

    def setup_wifi(self, cloud_provider, ssid, psk="", auth="wpa-psk"):
        """
        Set up WiFi credentials for demo firmware using its CLI
        This will only work with applications having this CLI.

        :param cloud_provider: Cloud provider in use
        :type cloud_provider: str
        :param ssid: Network SSID
        :type ssid: str
        :param psk: Network passkey
        :type psk: str
        :param auth: Network authentication method
        :type auth: str
        """
        if not ssid:
            self.logger.warning("No SSID given, doing nothing")
            return
        if auth not in WIFI_AUTHS.keys():
            self.logger.error("Invalid authentication: %s", auth)
            raise ProvisionerError("WiFi setup failed - invalid authentication")
        try:
            # Setup application firmware
            function = "demo-{}".format(cloud_provider)
            self.connect(function)
            # FIXME: Should not use low-level commands here, move to DemoFirmwareInterface
            demo_fw_version = self.fwinterface.demo_fw_command("version")
            # Read FW version first to increase chance of success
            if demo_fw_version and "." in demo_fw_version:
                self.logger.debug("Demo firmware version: %s", demo_fw_version)
            else:
                self.logger.error("Demo firmware reported invalid version: %s", demo_fw_version or None)

            fw_wifi_config_arguments = [ssid, psk, WIFI_AUTHS[auth]]
            response = self.fwinterface.demo_fw_command("wifi", fw_wifi_config_arguments)
            if not response.startswith("OK"):
                self.logger.error("Unexpected response from FW: %s", response)
                raise ProvisionerError("WiFi setup failed - unexpected response from application")
        except Exception as e:
            self.logger.error("Serial communication failure on port %s: %s", self.port, e)
            raise ProvisionerError("WiFi setup failed - communication error")
        finally:
            self.disconnect()

    def winc_upgrade(self, force_upgrade=False):
        """
        Upgrade the WINC1500 module using the bundled firmware

        :param force_upgrade: perform the upgrade regardless of the current version
        :type force_upgrade: boolean
        """
        # Bundled FW is:
        WINC_FW_VERSION_BUNDLED = "19.7.6"
        bin_file_name = os.path.join(self.installdir, "fw/winc/WINC1500_{0:s}.bin".format(WINC_FW_VERSION_BUNDLED))

        # Bundled certificates:
        tls_root_certs_file_name = os.path.join(self.installdir, "fw/winc/tls_root_cert.bin")

        # First check if its there already using the bridge that is in place, if there is one...
        if not force_upgrade:
            # Setup provisioning firmware
            self.connect("iotprovision")

            self.logger.info("Querying current WINC firmware version")
            winc_fw_version, winc_driver_version = self.fwinterface.winc_read_fw_version()
            self.logger.info("WINC firmware version: %s", winc_fw_version)
            self.logger.info("WINC driver version: %s", winc_driver_version)

            if version_parse(winc_fw_version) >= version_parse(WINC_FW_VERSION_BUNDLED):
                self.logger.info("WINC firmware is already up to date.")
                self.logger.info("Skipping upgrade.")
                self.disconnect()
                return

        # First check that we have a file and its readable
        with open(bin_file_name, "rb") as file:
            full_image_data = file.read()

        # And TLS certificates
        with open(tls_root_certs_file_name, "rb") as file:
            tls_root_certificate_data = file.read()
            length = len(tls_root_certificate_data)
            assert(length <= FlashMap.sector_size)  # This should never happen
            # The file produced by pywinc can be smaller than one sector, this API
            # requires exactly one sector, so extend it.
            tls_root_certificate_data += bytes([0xff] * (FlashMap.sector_size - length))

        # Put the upgrader-bridge FW in place
        self.connect("wincupgrade")

        # Now try to talk to it
        try:
            serialport = self.fwinterface.get_comport_handle()
            # Create the upgrade driver
            upgrader = WincUpgrade(serialport)

            current_version = "0.0.0"
            # Check connection first, unless irrelevant
            if not force_upgrade:
                self.logger.info("Checking WINC firmware...")
                status = upgrader.check_bridge()
                if status:
                    # Read out the FW version
                    current_version, driver_version = upgrader.read_firmware_version()
                else:
                    # Reset the MCU hosting the bridge
                    self.programmer.reset_target()

                    # Reset the WINC
                    # TODO: is this required?
                    #upgrader.reset()

            if version_parse(current_version) >= version_parse(WINC_FW_VERSION_BUNDLED) and not force_upgrade:
                self.logger.info("WINC firmware is already up to date.")
                self.logger.info("Skipping upgrade.")
            else:
                self.logger.info("Starting WINC firmware upgrade to version %s", WINC_FW_VERSION_BUNDLED)

                # Do the upgrade
                upgrader.upgrade_full_image(full_image_data)
                self.logger.info("WINC upgrade complete.")

                # Re-report firmware version
                fw_version, driver_version = upgrader.read_firmware_version()
                self.logger.info("WINC firmware version: %s", fw_version)
                self.logger.info("WINC driver version required: %s", driver_version)

                # Replace certificate sector which has now been reverted
                self.logger.info("Restoring WINC Root Certificate storage")
                upgrader.write_tls_root_certificate_sector(tls_root_certificate_data)
                self.disconnect()

        except Exception as e:
            self.logger.error("Serial communication failure on port %s: %s", self.port, e)
            self.disconnect()
            raise ProvisionerError("WINC upgrade failed - communication error")
        finally:
            # Restore provisioning firmware
            self.connect("iotprovision")


class ProvisionerAzure(Provisioner):
    """
    Azure provisioning mechanisms

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None,
                 installdir=os.path.abspath(os.path.dirname(__file__))):
        super().__init__(programmer, skip_program_provision_fw, port, installdir)
        self.cloud_provider = "azure"

    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        """
        Generate certificates

        :param force: Set to True to force regeneration
        :type force: boolean
        :param org_name: Organization name
        :type org_name: str
        :param root_common_name: Common name of Root
        :type root_common_name: str
        :param signer_common_name: Common name of Signer
        :type signer_common_name: str
        """
        if force or not os.path.isfile(Config.Certs.get_path("signer_ca_ver_cert_file")):
            self.logger.info("Creating root of trust...")
            self.create_root_of_trust(force=force, org_name=organization_name,
                                      root_common_name=root_common_name,
                                      signer_common_name=signer_common_name)
        else:
            self.logger.info("Signer CA verification certificate already exists")

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Do the actual provisioning for Azure

        :param force_new_device_certificate: Set to True to force new certificate
        :type force_new_device_certificate: boolean
        :param skip_program_provision_firmware: Set to True to skip programming
        :type skip_program_provision_firmware: boolean
        """
        # Setup provisioning firmware
        self.connect("iotprovision-{}".format(self.cloud_provider), skip_programming=skip_program_provision_firmware)

        # Do provisioning (using pyazureutils Provisioner)
        provider_provisioner = AzureCustomProvisioner(
            Config.Certs.get_path("root_ca_cert_file"),
            Config.Certs.get_path("signer_ca_key_file"),
            Config.Certs.get_path("signer_ca_cert_file"),
            Config.Certs.get_path("device_csr_file", self.serialnumber),
            Config.Certs.get_path("device_cert_file", self.serialnumber),
            force_new_device_certificate)

        device_id = provider_provisioner.provision(self.fwinterface)

        # Abort if the device ID was not returned
        if not device_id:
            self.logger.critical("Provisioning failed, aborted")
            raise ProvisionerError("Invalid ID returned while provisioning for Azure")

        # Store the resulting id for reference only
        device_id_filename = Config.Certs.get_path("azure_device_id_file", self.serialnumber)
        self.logger.debug("Storing device ID to '%s'", device_id_filename)
        self.store_iot_id(device_id, device_id_filename)

        # Change the disk link after reprovisioning
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider=self.cloud_provider,
                                key2_value=device_id)
        self.debugger_reboot_required = True
        self.logger.info("Done provisioning device '%s'", device_id)
        self.disconnect()

class ProvisionerGoogle(Provisioner):
    """
    Google provisioning mechanism

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None,
                 installdir=os.path.abspath(os.path.dirname(__file__))):
        super().__init__(programmer, skip_program_provision_fw, port, installdir)
        self.cloud_provider = "google"

    #pylint: disable=unused-argument
    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Do the actual provisioning for Google

        :param force_new_device_certificate: Set to True to force new certificate
        :type force_new_device_certificate: boolean
        :param skip_program_provision_firmware: Set to True to skip programming
        :type skip_program_provision_firmware: boolean
        """
        # Setup provisioning firmware
        self.connect("iotprovision-{}".format(self.cloud_provider), skip_programming=skip_program_provision_firmware)

        # Google requires no active provisioning.  Read out the ECC serialnumber.
        self.logger.info("Reading ECC serial number")
        ecc_serial_number = self.fwinterface.ecc_read_serialnumber()

        # Abort if the ECC serial number was not returned
        if not ecc_serial_number:
            self.logger.critical("Provisioning failed, aborted")
            raise ProvisionerError("Invalid ECC serial number returned while provisioning for Google")

        # Store the ECC serialnumber for reference only
        ecc_serial_number_filename = Config.Certs.get_path("ecc_serial_file", self.serialnumber)
        self.logger.debug("Storing ECC serialnumber to '%s'", ecc_serial_number_filename)
        self.store_iot_id(ecc_serial_number, ecc_serial_number_filename)

        # Change the disk link after reprovisioning
        kit_configure_disk_link(serialnumber=self.serialnumber, cloud_provider=self.cloud_provider,
                                key2_value=ecc_serial_number)
        self.debugger_reboot_required = True

        self.logger.info("Done provisioning device '%s'", ecc_serial_number)
        self.disconnect()

class ProvisionerAws(Provisioner):
    """
    AWS Microchip sandbox account provisioning mechanism

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    def __init__(self, programmer, skip_program_provision_fw=False, port=None,
                 installdir=os.path.abspath(os.path.dirname(__file__))):
        super().__init__(programmer, skip_program_provision_fw, port, installdir)
        self.cloud_provider = "aws"

    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        # Nothing to do for Sandbox
        return

    def _aws_provision(self, provisioner, skip_program_provision_firmware=False):
        # Setup provisioning firmware
        self.connect("iotprovision-{}".format(self.cloud_provider), skip_programming=skip_program_provision_firmware)

        # Do provisioning
        thingname = provisioner.provision(self.fwinterface)

        # Abort if the thing name was not returned
        if not thingname:
            self.logger.critical("Provisioning failed, aborted")
            raise ProvisionerError("Invalid thing name returned while provisioning for AWS")

        # Store the resulting thing name for reference only
        thingname_filename = Config.Certs.get_path("aws_thing_file", self.serialnumber)
        self.logger.debug("Storing thingname to '%s'", thingname_filename)
        self.store_iot_id(thingname, thingname_filename)
        self.disconnect()
        return thingname

    #pylint: disable=unused-argument
    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Provisioning for AWS

        :param force_new_device_certificate: Set to True to force new certificate
        :type force_new_device_certificate: boolean
        :param skip_program_provision_firmware: Set to True to skip programming
        :type skip_program_provision_firmware: boolean
        """
        device_cert_file = Config.Certs.get_path("device_cert_file_sandbox", self.serialnumber)
        provider_provisioner = AwsSandboxProvisioner(
            # The signer certificate for sandbox will come from the ECC compressed data so it will differ
            # for each ECC/kit
            Config.Certs.get_path("signer_cert_file_sandbox", self.serialnumber),
            device_cert_file,
            force_new_device_certificate)

        thingname = self._aws_provision(provider_provisioner, skip_program_provision_firmware)

        # Change the disk link after reprovisioning
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider=self.cloud_provider,
                                key2_value=thingname)
        self.debugger_reboot_required = True

        self.logger.info("Done provisioning thing '%s'", thingname)


class ProvisionerAwsMar(ProvisionerAws):
    """
    AWS MAR provisioning mechanism

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    def setup_account(self, profile_name, force_setup):
        """
        Prepare AWS account for MAR
        """
        self.logger.info("Create AWS policy using MAR")
        create_policy_mar(profile_name)
        # Store profile name for later
        self.aws_profile_name = profile_name

    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        """
        Create root & signer certificates, register signer with AWS.
        Only do this once.

        :param force: Set to True to force regeneration
        :type force: boolean
        :param org_name: Organization name
        :type org_name: str
        :param root_common_name: Common name of Root
        :type root_common_name: str
        :param signer_common_name: Common name of Signer
        :type signer_common_name: str
        """
        if force or not os.path.isfile(Config.Certs.get_path("signer_ca_ver_cert_file")):
            self.create_root_of_trust(force=force, org_name=organization_name,
                                      root_common_name=root_common_name,
                                      signer_common_name=signer_common_name)
        else:
            self.logger.info("Using previously generated certificates in %s", Config.Certs.certs_dir)

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Provisioning for AWS

        :param force_new_device_certificate: Set to True to force new certificate
        :type force_new_device_certificate: boolean
        :param skip_program_provision_firmware: Set to True to skip programming
        :type skip_program_provision_firmware: boolean
        """
        device_cert_file = Config.Certs.get_path("device_cert_file", self.serialnumber)
        provider_provisioner = AwsCustomProvisioner(
            Config.Certs.get_path("signer_ca_key_file"),
            Config.Certs.get_path("signer_ca_cert_file"),
            Config.Certs.get_path("device_csr_file", self.serialnumber),
            device_cert_file,
            force_new_device_certificate)

        thingname = self._aws_provision(provider_provisioner, skip_program_provision_firmware)

        # Register device certificate without CA for custom provisioning with MAR
        aws_mar_tool = aws_mar(aws_profile=self.aws_profile_name)
        aws_mar_tool.create_device(certificate_file=device_cert_file,
                                   policy_name="zt_policy", thing_type=None)

        # Change the disk link after reprovisioning
        # Note: disk link will not lead to data in the user's custom account.
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider='awscustom',
                                key2_value=thingname)
        self.debugger_reboot_required = True

        self.logger.info("Done provisioning thing '%s'", thingname)


class ProvisionerAwsJitr(ProvisionerAws):
    """
    AWS JITR provisioning mechanism

    :param programmer: Programmer to use
    :type programmer: object
    :param skip_program_provision_fw: Set to True to skip programming the target
    :type skip_program_provision_fw: boolean
    :param port: Serial port to use
    :type port: str
    :param installdir: Path to operate in
    :type installdir: str
    :raises: KitConnectionError exception if none or multiple kits found, its value will contain the list of kits.
    """
    def setup_account(self, profile_name, force_setup):
        """
        Prepare AWS account for JITR

        :param profile_name: AWS profile name
        :type profile_name: str
        :param force_setup: Set to True to force account setup
        :type force_setup: boolean
        """
        self.logger.info("AWS JITR account registration")
        setup_aws_jitr_account(force=force_setup)
        self.aws_profile_name = profile_name

    def generate_certificates(self, force, organization_name, root_common_name, signer_common_name):
        """
        Create root & signer certificates, register signer with AWS.
        Only do this once.

        :param force: Set to True to force regeneration
        :type force: boolean
        :param org_name: Organization name
        :type org_name: str
        :param root_common_name: Common name of Root
        :type root_common_name: str
        :param signer_common_name: Common name of Signer
        :type signer_common_name: str
        """
        if force or not os.path.isfile(Config.Certs.get_path("signer_ca_ver_cert_file")):
            self.aws_custom_register(force=force, aws_profile=self.aws_profile_name,
                                     org_name=organization_name,
                                     root_common_name=root_common_name,
                                     signer_common_name=signer_common_name)
        else:
            self.logger.info("Using previously generated certificates in %s", Config.Certs.certs_dir)
            self.aws_custom_register_signeronly(self.aws_profile_name)

    def aws_custom_register(self, force, aws_profile="default", org_name=DEFAULT_ORGANIZATION_NAME,
                            root_common_name=DEFAULT_ROOT_COMMON_NAME, signer_common_name=DEFAULT_SIGNER_COMMON_NAME):
        """
        Create certificate files and register signer with AWS. For custom provisioning only.

        :param force: Set to True to force regeneration
        :type force: boolean
        :param aws_profile: AWS profile name
        :type aws_profile: str
        :param org_name: Organization name
        :type org_name: str
        :param root_common_name: Common name of Root
        :type root_common_name: str
        :param signer_common_name: Common name of Signer
        :type signer_common_name: str
        """
        self.create_root_of_trust(force=force, org_name=org_name, root_common_name=root_common_name,
                                  signer_common_name=signer_common_name)

        register_signer(signer_ca_key_path=Config.Certs.get_path("signer_ca_key_file"),
                        signer_ca_cert_path=Config.Certs.get_path("signer_ca_cert_file"),
                        signer_ca_ver_cert_path=Config.Certs.get_path("signer_ca_ver_cert_file"),
                        aws_profile=aws_profile)


    def aws_custom_register_signeronly(self, aws_profile="default"):
        """
        Register signer with AWS. For custom provisioning only.

        :param aws_profile: AWS profile name
        :type aws_profile: str
        """
        register_signer(signer_ca_key_path=Config.Certs.get_path("signer_ca_key_file"),
                        signer_ca_cert_path=Config.Certs.get_path("signer_ca_cert_file"),
                        signer_ca_ver_cert_path=Config.Certs.get_path("signer_ca_ver_cert_file"),
                        aws_profile=aws_profile)

    def do_provision(self, force_new_device_certificate=False, skip_program_provision_firmware=False):
        """
        Provisioning for AWS

        :param force_new_device_certificate: Set to True to force new certificate
        :type force_new_device_certificate: boolean
        :param skip_program_provision_firmware: Set to True to skip programming
        :type skip_program_provision_firmware: boolean
        """
        device_cert_file = Config.Certs.get_path("device_cert_file", self.serialnumber)
        provider_provisioner = AwsCustomProvisioner(
            Config.Certs.get_path("signer_ca_key_file"),
            Config.Certs.get_path("signer_ca_cert_file"),
            Config.Certs.get_path("device_csr_file", self.serialnumber),
            device_cert_file,
            force_new_device_certificate)

        thingname = self._aws_provision(provider_provisioner, skip_program_provision_firmware)

        # Change the disk link after reprovisioning
        kit_configure_disk_link(serialnumber=self.serialnumber,
                                cloud_provider='awscustom',
                                key2_value=thingname)
        self.debugger_reboot_required = True

        self.logger.info("Done provisioning thing '%s'", thingname)
