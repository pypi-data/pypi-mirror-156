"""
This script implements the "sandbox" AWS provisioning method, using device certificate from ECC.
It is intended to be invoked from iotprovison, but can also be run stand-alone.
"""
import os
from logging import getLogger
import hashlib
import binascii
from cryptography import x509
from cryptography.hazmat.primitives import serialization

from pytrustplatform.ecc_cert_builder import build_certs_from_ecc
from pyawsutils.aws_cloudformation import MCHP_SANDBOX_ENDPOINT


class AwsSandboxProvisioner:
    """
    Provides "sandbox" provisioning for AWS cloud

    :param signer_cert_file: Path to file containing the signer certificate
    :type signer_cert_file: str (path)
    :param device_cert_file: Path to the file to write the generated device certificate to
    :type device_cert_file: str (path)
    :param force_new_device_certificate: Force creation of new device certificate even if it exists already
    :type force_new_device_certificate: boolean, optional
    """
    def __init__(self, signer_cert_file, device_cert_file="device_aws_sandbox.pem",
                 force_new_device_certificate=False):
        """

        """
        self.logger = getLogger(__name__)
        self.signer_cert_file = signer_cert_file
        self.device_cert_file = device_cert_file
        self.force_new_device_certificate = force_new_device_certificate

    def provision(self, fwinterface):
        """
        Do the actual provisioning
        Read out device certificate from kit, save it to file, extract "thing name"
        (AKA subject key identifier), save these items to WINC flash for easy access by application.

        :param fwinterface: Firmware interface
        :type fwinterface: :class: ProvisioningFirmwareInterface
        :return: "Thing name" (Subject Key Identifier) if successful, else None
        :rtype: str
        """
        thing_name = None
        self.logger.info("Erasing WINC TLS certificate sector")
        fwinterface.winc_erase_tls_certificate_sector()

        if self.force_new_device_certificate or not os.path.isfile(self.device_cert_file):
            self.logger.info("Generating certificates")
        device_cert, signer_cert = build_certs_from_ecc(fwinterface.get_firmware_driver(),
                                                        self.signer_cert_file,
                                                        self.device_cert_file,
                                                        force=self.force_new_device_certificate)
        try:
            ski = device_cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_KEY_IDENTIFIER).value.digest
            thing_name = binascii.b2a_hex(ski).decode()
        except x509.ExtensionNotFound:
            pubkey = device_cert.public_key().public_bytes(encoding=serialization.Encoding.DER,
                                                           format=serialization.PublicFormat.SubjectPublicKeyInfo)
            thing_name = hashlib.sha1(pubkey[-65:]).hexdigest()

        # FIXME: The WINC specific code should be split out, so we can
        #        use this for cellular provisioning also.

        # Add device certificate for storage in WINC
        self.logger.info("Sending Device Certificate")
        fwinterface.winc_add_client_certificate(device_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        # Add signer certifate for storage in WINC
        self.logger.info("Sending Signer Certificate")
        fwinterface.winc_add_client_certificate(signer_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        self.logger.info("Transferring certificates to WINC")
        fwinterface.winc_write_tls_certificates_sector()

        self.logger.info("Saving thing name in WINC")
        fwinterface.winc_write_thing_name(thing_name)

        self.logger.debug("Locking ECC slots 10-12")
        for slot in [10, 11, 12]:
            fwinterface.ecc_lock_slot(slot)

        #Endpoint for Microchip sandbox account
        endpoint = MCHP_SANDBOX_ENDPOINT
        self.logger.info("Saving AWS endpoint in WINC")
        fwinterface.winc_write_endpoint_name(endpoint)

        return thing_name
