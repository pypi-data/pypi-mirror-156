"""
iotprovision constant config settings.
"""
import os

#TODO: populate from config file (yaml)?

class Config:
    """
    Global configuration settings. Do not instantiate object from this.
    """
    class Certs:
        """
        Certificate store settings and functions.
        Usage example:

        .. code-block:: python

            from config import Config
            root_ca_cert_filename = Config.Certs.get_path("root_ca_cert_file")
            device_filename = Config.Certs.get_path("device_cert_file", serial_num)
        """
        # TODO - find a way for this to not be expanded by Sphinx
        certs_dir = os.path.join(os.path.expanduser("~"), ".microchip-iot")
        # Common certificate files
        root_ca_key_file = "root-ca.key"
        root_ca_cert_file = "root-ca.crt"
        signer_ca_key_file = "signer-ca.key"
        signer_ca_csr_file = "signer-ca.csr"
        signer_ca_cert_file = "signer-ca.crt"
        signer_ca_ver_cert_file = "signer-ca-verification.crt"
        # Device specic certificate files
        device_csr_file = "device.csr"
        device_cert_file = "device.crt"
        signer_cert_file = "signer.crt"
        device_cert_file_sandbox = "device_sandbox.crt"
        signer_cert_file_sandbox = "signer_sandbox.crt"
        # Other device specific files
        aws_thing_file = "aws-thing-name.txt"
        azure_device_id_file = "azure-device-id.txt"
        ecc_serial_file = "ecc_serial_number.txt"
        root_certs_backup_file = "root_certs_backup.bin"

        @classmethod
        def get_path(cls, item, subdir=None):
            """
            Get pathname for file in certificate store.

            :param item: Attribute name
            :type item: str
            :param subdir: Subdirectory of certs_dir, mandatory for device specific files
            :type subdir: str
            :returns: Absolute pathname for specified item
            :raises: AttributeError if nonexistent attribute
            """
            if subdir:
                # Device specific files must be in unique per-device subfolder
                return os.path.abspath(os.path.join(cls.certs_dir, subdir, getattr(cls, item)))
            return os.path.abspath(os.path.join(cls.certs_dir, getattr(cls, item)))

    # Define for other config items here
