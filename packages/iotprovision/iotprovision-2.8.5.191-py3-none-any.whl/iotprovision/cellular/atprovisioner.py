"""
IoT provisioning API for Sequans modem
Protocol port must be opened in advance
"""

from logging import getLogger
from packaging.version import parse as version_parse

from ..provisioner import ProvisionerError
from .atdriver import AtDriver

class AtProvisioner():
    """
    AtProvisioner class for Sequans modem. To manage bridge status automatically, instantiate this class using 'with':

    with AtProvisioner(fwinterface) as atprovisioner:
        ...

    FW interface's port must be opened in advance.

    :param fwinterface: Firmware interface
    """
    def __init__(self, fwinterface):
        self.logger = getLogger(__name__)
        self.fwinterface = fwinterface
        self.atdriver = AtDriver(fwinterface)
        # Set error verbosity in modem if debug logging
        self.logger.debug("Set modem verbose error response: %s", self.atdriver.command("AT+CMEE=2"))

    # Support 'with ... as ...' construct
    def __enter__(self):
        # Bridge status management delegated to atdriver
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Bridge status management delegated to atdriver
        pass

    def set_provider(self, provider):
        """
        Set network provider
        """
        if not provider:
            return
        cmd = 'AT+SQNCTM="{}"'.format(provider)
        self.logger.debug("Set provider: %s", cmd)
        response = self.atdriver.command(cmd)
        if response[-1] != "OK":
            self.logger.error("Set network provider failed: %s", response)
            raise ProvisionerError("Set network provider failed")

    def set_frequency_bands(self, provider, frequency_bands):
        """
        Set frequency bands for given provider

        :param provider: Network provider to select bands for
        :param frequency_bands: List of frequency bands to scan
        """
        if not frequency_bands:
            return
        cmd = 'AT+SQNBANDSEL=0,"{}","{}"'.format(provider, ",".join(frequency_bands))
        self.logger.debug("Select frequency bands: %s", cmd)
        response = self.atdriver.command(cmd)
        if response[-1] != "OK":
            raise ProvisionerError("Select frequency bands failed: {}".format(response))

    def write_slot(self, datatype, cert, slot):
        """
        Write a certificate or private key to modem NVM slot.

        :param datatype: "certificate", "privatekey", or "strid" (don't know what the latter is used for)
        :param cert: Certificate or private key in PEM format
        :param slot: Slot number to write to
        """
        try:
            # self.erase_slot(datatype, slot)  #This fails if slot already empty, seems not required.
            self.logger.debug("Writing %d bytes %s to slot %d", len(cert), datatype, slot)
            self.atdriver.write_nvm(datatype, slot, cert)
        except Exception as e:
            self.logger.error("Failed to write %s to slot %d: %s", datatype, slot, e)
            raise e

    def erase_slot(self, datatype, slot):
        """
        Erase a single slot.

        :param datatype: "certificate", "privatekey", or "strid" (don't know what the latter is used for)
        :param slot: Slot number to erase
        """
        self.logger.debug("Erasing %s in slot %d", datatype, slot)
        return self.atdriver.write_nvm(datatype, slot)

    def set_security_profile(self, spid=1, ciphersuites=None, server_ca=19, client_cert=0,
                                 client_key=0, client_key_storage=1):
        """ Set up a security profile.

        TODO we can put cipher suite settings back once this is supported

        Note that if no ciphers are provided nothing should be printed in the
        command -> no "". This is a breaking change between 5.2 and 5.4 FW.

        FW 5.2 allowed AT+SQNSPCFG=1,3,"",3,1,1,1 but
        FW 5.4 requires AT+SQNSPCFG=1,3,,3,1,1,1
        FW 5.4.1.0-50495 for ECC support adds more parameters AT+SQNSPCFG=1,2,"0xc02c",1,19,0,0,"","",1

        +SQNSPCFG:<spId>,<version>,<cipherSpecs>,<certValidLevel>,<caCertificateID>,<clientCertificateID>,
        <clientPrivateKeyID>,<psk>,??,<clientPrivateKeyStorage>

        :param spid: security profile identifier(1-6), defaults to 1
        :type spid: int, optional
        :param ciphersuites: set of ciphersuites, 0xc02b = ECDHE-ECDSA-AES128-GCM-SHA256, defaults to none
        :type ciphersuites: list, optional
        :param server_ca: Server CA certificate slot [0-19], defaults to 19
        :type server_ca: int, optional
        :param client_cert: Client certificate slot [0-19], defaults to 0
        :type client_cert: int, optional
        :param client_key: Client private key slot or key ID [0-19], defaults to 0
        :type client_key: int, optional
        :param client_key_storage: Set to 1 for storage of private key in ECC and to 0 for storage in Sequans modem,
            defaults to 1
        :type client_key_storage: int, optional
        :rtype: int
        """
        if ciphersuites:
            cipher_str = f"\"{';'.join(ciphersuites)}\""
        else:
            cipher_str = ""
        tls_version = 2   # (1.2). Can parametrize this if it is required at some point.
        cmd = f'AT+SQNSPCFG={spid},{tls_version},{cipher_str},1,{server_ca},'\
            f'{client_cert},{client_key},"","",{client_key_storage}'
        self.logger.debug("Set security profile, cmd = %s", cmd)
        response = self.atdriver.command(cmd)
        if response[-1] != "OK":
            raise ProvisionerError(f"Set security profile failed: {response}")
