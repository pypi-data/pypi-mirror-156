"""
Manage content of WINC root certificate sector. Note that this module uses the
IoT provisioning firmware to access the WINC, not the WINC bridge.
"""

from logging import getLogger
from .winc.winc_flash_map import FlashMap
from .winc.winc_certs import RootCertStorage


class WincRootCerts:
    """
    Class implementing the root certificate store manager.
    """

    def __init__(self, fwinterface, backupfile, factoryfile):
        """
        :param fwinterface: Provisioning firmware interface
        :param backupfile: Backup file for root certificates sector
        :param factoryfile: Factory defaults file
        """
        self.logger = getLogger(__name__)
        self.fwinterface = fwinterface
        self.backupfile = backupfile
        self.factoryfile = factoryfile
        self.rootsect_offset = FlashMap.tls_root_cert_offset
        self.rootsect_size = FlashMap.tls_root_cert_size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return

    def write_rootcerts_blob(self, blob):
        """
        Write root certificate sector from a blob. Save original content to backup file
        :param blob: Binary data to write, size max one sector
        :return: Original data in sector
        """
        if len(blob) > self.rootsect_size:
            raise ValueError(f"Root certificate image too large: {len(blob)}/{self.rootsect_size}")
        backup = self.fwinterface.winc_read(self.rootsect_offset, self.rootsect_size)
        self.fwinterface.winc_erase_sector(self.rootsect_offset)
        self.fwinterface.winc_write(self.rootsect_offset, blob)
        self.logger.debug("Writing backup to file %s", self.backupfile)
        with open(self.backupfile, "wb") as f:
            f.write(backup)
        return backup

    def write_rootcerts_file(self, filename):
        """
        Write root certificate sector from a binary file, save backup to file
        :param filename: Name of blob binary file
        """
        self.logger.debug("Writing blob from file %s", filename)
        with open(filename, "rb") as f:
            blob = f.read()
        return self.write_rootcerts_blob(blob)

    def build_rootcerts_blob(self, filelist):
        """
        Build a blob from a list of certificate files
        :param filelist: List of certificate files, may be in PEM or DER format
        :return: blob for writing to WINC
        """
        builder = RootCertStorage()
        self.logger.info("Building blob from %d certificates", len(filelist))
        for file in filelist:
            self.logger.debug("Adding certificate from file: %s", file)
            builder.add_certificate(file)
        blob = builder.build()
        self.logger.info("Blob size: %d bytes", len(blob))
        return blob
