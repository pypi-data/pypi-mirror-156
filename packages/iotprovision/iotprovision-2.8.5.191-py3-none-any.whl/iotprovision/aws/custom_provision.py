"""
This script implements the "custom" AWS provisioning method, using
self-generated root and signer certificates.
It is intended to be invoked from iotprovison, but can also be run stand-alone.
"""

import os
import binascii
from logging import getLogger
import boto3
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from pytrustplatform.device_cert_builder import build_device_cert


class AwsCustomProvisioner:
    """
    Provides "custom"/JITR (Just In Time Registration) provisioning for AWS

    :param signer_ca_key_file: Path to file containing signer Certificate Authority private key
    :type signer_ca_key_file: str (path)
    :param signer_ca_cert_file: Path to file containing signer Certificate Authority certificate file
    :type signer_ca_cert_file: str (path)
    :param device_csr_file: Path to the file to write the generated Certificate Signer Request to
    :type device_csr_file: str (path)
    :param device_cert_file: Path to the file to write the generated device certificate to
    :type device_cert_file: str (path)
    :param force_new_device_certificate: Force creation of new device certificate even if it exists already
    :type force_new_device_certificate: boolean, optional
    """
    def __init__(self, signer_ca_key_file, signer_ca_cert_file, device_csr_file,
                 device_cert_file, force_new_device_certificate=False):
        self.logger = getLogger(__name__)
        # Setup cryptography backend
        self.crypto_be = default_backend()
        self.signer_ca_key_file = signer_ca_key_file
        self.signer_ca_cert_file = signer_ca_cert_file
        self.device_csr_file = device_csr_file
        self.device_cert_file = device_cert_file
        self.force_new_device_certificate = force_new_device_certificate

    def provision(self, fwinterface):
        """
        Do the actual provisioning.
        This will generate a device certificate, and save it along with the CA signer certificate in WINC flash
        Returns the "Thing name" (Subject Key Identifier) if successful.
        Generated certificates and thing name are saved to files as well.

        :param fwinterface: Firmware interface driver
        :type fwinterface: :class:`ProvisioningFirmwareInterface`
        :return: "Thing name" (Subject Key Identifier) if successful, else None
        :rtype: str
        """
        # Get endpoint from AWS
        iot_client = boto3.client('iot')
        response = iot_client.describe_endpoint()
        aws_endpoint_address = response['endpointAddress']

        self.logger.info("Loading Signer CA certificate")
        with open(self.signer_ca_cert_file, 'rb') as certfile:
            self.logger.info("    Loading from %s", certfile.name)
            signer_ca_cert = x509.load_pem_x509_certificate(certfile.read(), self.crypto_be)

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

        thing_name = None
        for extension in device_cert.extensions:
            if extension.oid._name != 'subjectKeyIdentifier':
                continue # Not the extension we're looking for, skip
            thing_name = binascii.b2a_hex(extension.value.digest).decode('ascii')

        self.logger.info("Provisioning device with AWS IoT credentials")

        # FIXME: The WINC specific code should be split out, so we can
        #        use this for cellular provisioning also.
        self.logger.info("Sending Device Certificate")
        fwinterface.winc_add_client_certificate(device_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        self.logger.info("Sending Signer Certificate")
        fwinterface.winc_add_client_certificate(signer_ca_cert.public_bytes(encoding=serialization.Encoding.DER).hex())

        self.logger.info("Transferring certificates to WINC")
        fwinterface.winc_write_tls_certificates_sector()

        self.logger.info("Saving thing name in WINC")
        fwinterface.winc_write_thing_name(thing_name)

        self.logger.info("Saving AWS endpoint in WINC")
        fwinterface.winc_write_endpoint_name(aws_endpoint_address)
        self.logger.info("AWS endpoint : %s", aws_endpoint_address)

        return thing_name
