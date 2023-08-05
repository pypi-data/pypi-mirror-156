"""
This script implements the "custom" Azure provisioning method, using
self-generated root and signer certificates.
It is intended to be invoked from iotprovison, but can also be run stand-alone.
"""

import os
from logging import getLogger
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from pytrustplatform.device_cert_builder import build_device_cert

class AzureCustomProvisioner:
    """
    Azure specific provisioning steps

    :param root_ca_cert_file: Path to file containing root Certificate Authority certificate file
    :type root_ca_cert_file: str (path)
    :param signer_ca_key_file: Path to file containing signer Certificate Authority private key
    :type signer_ca_key_file: str (path)
    :param signer_ca_cert_file: Path to file containing signer Certificate Authority certificate file
    :type signer_ca_cert_file: str (path)
    :param device_csr_file: Path to the file to write the generated Certificate Signer Request to
    :type device_csr_file: str (path)
    :param device_cert_file: Path to the file to write the generated device certificate to
    :type device_cert_file: str (path)
    :param force_new_device_certificate: Force re-creating already existing device certificate
    :type force_new_device_certificate: boolean
    """
    def __init__(self, root_ca_cert_file, signer_ca_key_file,
                 signer_ca_cert_file, device_csr_file, device_cert_file,
                 force_new_device_certificate=False):
        self.root_ca_cert_file = root_ca_cert_file
        self.signer_ca_key_file = signer_ca_key_file
        self.signer_ca_cert_file = signer_ca_cert_file
        self.device_csr_file = device_csr_file
        self.device_cert_file = device_cert_file
        self.force_new_device_certificate = force_new_device_certificate

        self.logger = getLogger(__name__)
        self.crypto_be = default_backend()


    def provision(self, fwinterface):
        """
        Do the actual provisioning.

        This will generate a device certificate, and save it along with the CA signer certificate in WINC flash
        Returns the "Thing name" (Subject Key Identifier) if successful.
        Generated certificates and thing name are saved to files as well.

        :param fwinterface: Firmware fwinterface driver
        :type fwinterface: :class:`ProvisioningFirmwareInterface`
        :return: "Thing name" (Subject Key Identifier) if successful, else None
        :rtype: str
        """

        self.logger.info("Loading root CA certificate")
        with open(self.root_ca_cert_file, 'rb') as f:
            self.logger.info("    Loading from %s", f.name)
            root_ca_cert = x509.load_pem_x509_certificate(f.read(), self.crypto_be)

        self.logger.info("Loading signer CA certificate")
        with open(self.signer_ca_cert_file, 'rb') as f:
            self.logger.info("    Loading from %s", f.name)
            signer_ca_cert = x509.load_pem_x509_certificate(f.read(), self.crypto_be)

        self.logger.info("Erase WINC TLS certificate sector")
        fwinterface.winc_erase_tls_certificate_sector()

        if self.force_new_device_certificate or not os.path.isfile(self.device_cert_file):
            self.logger.info("Generating device certificates")
        device_cert = build_device_cert(fwinterface.get_firmware_driver(),
                                        self.signer_ca_cert_file,
                                        self.signer_ca_key_file,
                                        self.device_csr_file,
                                        self.device_cert_file,
                                        force=self.force_new_device_certificate)

        # Set the Device ID to the subject common name (will be "sn<ECC serial>")
        device_id = device_cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[0].value

        self.logger.info("Provisioning device with credentials")

        self.logger.info("Send Device Certificate")
        fwinterface.winc_add_client_certificate(device_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        self.logger.info("Send Signer Certificate")
        fwinterface.winc_add_client_certificate(signer_ca_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        self.logger.info("Transfer certificates to WINC")
        fwinterface.winc_write_tls_certificates_sector()

        # TODO we have to revisit this once we know exactly what we need to program
        # here for the connection URL and the device ID
        # """
        # write_device_id(device_id)
        # print('    Done.\n')
        # """
        # """
        # write_endpoint_name(AWSEndpointaddress)
        # print ("AWS endpoint : ", AWSEndpointaddress)
        # """
        ############################################################################

        return device_id
