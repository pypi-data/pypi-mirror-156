"""
Collection of firmware Serial-port-based communication interface classes

The class is instantiated with kit_info from pykitcommader.kitprotocols.setup_kit()
and uses the kit_info porotocol_class to actually send FW commands to the kit.

"""

import binascii
import functools
from time import sleep
from logging import getLogger
from pyedbglib.serialport.serialcdc import SerialCDC
from pykitcommander.kitcommandererrors import PortError, KitCommunicationError, PykitcommanderError
from .winc.winc_flash_map import FlashMap
from .winc.winc_certs import ClientCertStorage
from .eccstorage import EccStorage


ASCII_EOT = b'\x04'

class ApplicationFirmwareInterface:
    """
    Base class for firmware interfaces
    Supports open, close, and get_comport_handle

    :param kit_info: Kit information from pykitcommander
    :type kit_info: dict
    :param programmer: Programmer to use
    :type programmer: object
    :param port: Serial port to connect to
    :type port: str, optional, defaults to the active kit
    :param stopbits: Number of stopbits to use
    :type stopbits: int, optional, defaults to 1
    :param encoding: Text encoding to use
    :type encoding: str, optional, defaults to UTF-8
    """
    def __init__(self, kit_info, programmer, port=None, stopbits=1, encoding="UTF-8"):
        # FIXME: stopbits should come from kit_info
        self.kit_info = kit_info
        self.programmer = programmer
        self.port = port or self.kit_info["serial_port"]
        self.com = None
        self.stopbits = stopbits
        self.encoding = encoding
        self.fwdriver = None
        self.eccstorage = EccStorage(self)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self):
        """
        Open serial port using values set during constuction
        """
        self.com = SerialCDC(self.port, self.kit_info["protocol_baud"], timeout=10, stopbits=self.stopbits)
        # Instantiate protocol driver class if this firmware interface has one.
        protocol_class = self.kit_info.get("protocol_class")
        self.fwdriver = protocol_class(self.com) if protocol_class else None

    def close(self):
        """
        Close serial port
        """
        if self.com:
            self.com.close()
        self.com = None
        self.fwdriver = None

    def get_comport_handle(self):
        """
        Get serial port handle

        :return: handle to serial port in use by this protocol
        """
        return self.com

    def get_firmware_driver(self):
        """
        Get firmware driver handle

        :return: handle to firmware driver from pykitcommander
        """
        return self.fwdriver

class WincUpgradeFirmwareInterface(ApplicationFirmwareInterface):
    """
    Interface to WINC upgrade firmware

    :param kit_info: Kit information from pykitcommander
    :type kit_info: dict
    :param programmer: Programmer to use
    :type programmer: object
    :param port: Serial port to connect to
    :type port: str, optional, defaults to the active kit
    :param stopbits: Number of stopbits to use
    :type stopbits: int, optional, defaults to 2
    :param encoding: Text encoding to use
    :type encoding: str, optional, defaults to UTF-8
    """
    DEFAULT_BAUD = 115200
    def __init__(self, kit_info, programmer, port=None, stopbits=2, encoding="UTF-8"):
        # FIXME: stopbits should come from kit_info
        super().__init__(kit_info, programmer, port=port, stopbits=stopbits, encoding=encoding)
        self.logger = getLogger(__name__)

    def read_fw_version(self):
        """
        Dummy get FW version.
        Needs to be present because called from protocol-independent part of Provisioner.
        """
        return "Unknown"



class ProvisioningFirmwareInterface(ApplicationFirmwareInterface):
    """
    Interface to provisioning firmware

    Implementation of the provisioning firmware communication protocol.

    Actual firmware interaction is delegated to firmware driver supplied by pykitcommander:
    fwdriver.firmware_command(command, [<arg-list>][, blob])
    where args can be either integer, bytes, or str

    :param kit_info: Kit information from pykitcommander
    :type kit_info: dict
    :param programmer: Programmer to use
    :type programmer: object
    :param port: Serial port to connect to
    :type port: str, optional, defaults to the active kit
    :param stopbits: Number of stopbits to use
    :type stopbits: int, optional, defaults to 1
    :param encoding: Text encoding to use
    :type encoding: str, optional, defaults to UTF-8
    """
    DEFAULT_BAUD = 115200

    # ECC slots can only be written with complete words
    ECC_SLOT_WORD_SIZE_BYTES = 4

    def __init__(self, kit_info, programmer, port=None, stopbits=1, encoding="UTF-8"):
        super().__init__(kit_info, programmer, port=port, stopbits=stopbits, encoding=encoding)
        self.logger = getLogger(__name__)
        self.bridge_mode = False
        self.tlsblob = ClientCertStorage()

    def _status_led(self, func):
        """
        Wrapper for fwdriver.firmware_command(), to decorate with LED status indication
        LED usage;
        DATA (yellow) => in firmware call
        ERROR (red)   => error occured, will remain on
        :param func: Function to wrap
        """
        def setled(led, state):
            """
            Local set LED state function. Cannot use firmware_command() here as it would
            lead to infinite recursion.
            """
            led = self._get_led_name(led)
            self.com.write((f"MC+SETLED={led},{state}\r\n").encode(self.encoding))
            # The following is to consume and ignore any response from above command
            self.com.read_until(b'\n')
            sleep(0.05)
            self.com.read(self.com.in_waiting)
        @functools.wraps(func)
        def wrapper_status_led(*args, **kwargs):
            """
            The actual wrapper function
            """
            try:
                setled("DATA", "ON")
                rvalue = func(*args, **kwargs)
                if rvalue.startswith("ERROR"):
                    setled("ERROR", "ON")
            except Exception as e:
                setled("ERROR", "ON")
                raise e
            finally:
                setled("DATA", "OFF")
            return rvalue
        return wrapper_status_led

    def open(self):
        super().open()

        # Synchronize with firmware CLI
        self.fwdriver.synchronize()

        # LED CONN (green) => provisioning firmware session active
        self.set_led_status("CONN", "ON")
        # Use wrapper for firmware_command() to give status LED indications
        # The line below will cause LED decoration to happen
        # Removimg the line below is all it takes to drop it.
        self.fwdriver.firmware_command = self._status_led(self.fwdriver.firmware_command)

    def close(self):
        if self.com:
            # Write 'LED off' command directly to port to avoid timeout waiting for response if
            # firmware is incapable of responding properly
            self.com.write(f"MC+SETLED={self._get_led_name('CONN')},OFF\n".encode(self.encoding))
        super().close()

    def ecc_read_serialnumber(self):
        """
        Reads the ECC serialnumber

        :return: ECC serialnumber
        :rtype: str
        """
        self.logger.info("ECC Read serial number")
        return self.fwdriver.firmware_command("MC+ECC+SERIAL")

    def ecc_read_public_key(self):
        """
        Reads the public key

        :return: Public key
        :rtype: str
        """
        self.logger.info("ECC read device public key")
        return self.fwdriver.firmware_command("MC+ECC+GENPUBKEY")

    def ecc_read_slot(self, slot_number, num_bytes=None):
        """
        Read contents of a slot on the ECC

        :param slot_number: ECC slot to read from
        :type slot_number: int
        :param num_bytes: Number of bytes to read, or omit for entire slot
        :type num_bytes: int
        :return: contents of slot
        """
        args = [slot_number]
        if num_bytes:
            args.append(num_bytes)
        self.logger.debug("ECC read slot %d", slot_number)
        return binascii.unhexlify(self.fwdriver.firmware_command("MC+ECC+READ", args))

    def ecc_write_slot(self, slot_number, data):
        """
        Write data to ECC slot.

        :param num_bytes: Number of bytes to write. Note slot length depends on slot number.
        :type num_bytes: int
        :param data: Data to write
        """
        self.logger.debug("ECC write %d bytes to slot %d", len(data), slot_number)
        # Read entire slot, needed to determine slot length
        slotdata = self.ecc_read_slot(slot_number)
        slotsize = len(slotdata)
        length = len(data)
        if length > len(slotdata):
            raise ValueError(f"Data length {length} exceeds slot {slot_number} length {len(slotdata)}")
        # TODO: Maybe truncate blob to data length plus 32-bit ECC word alignment.
        # For now writing entire slot
        blob = data + slotdata[length:]
        return self.fwdriver.firmware_command("MC+ECC+WRITEBLOB", [slot_number, slotsize], binascii.hexlify(blob))

    def ecc_lock_slot(self, slot_number):
        """
        Lock an ECC slot.
        Note: Locking ECC slots can not be undone!

        :param slot_number: Slot mumber to lock.
        :type slot_number: int
        """
        self.logger.info("ECC lock slot %d", slot_number)
        return self.fwdriver.firmware_command("MC+ECC+LOCK", [slot_number])

    def ecc_sign_digest(self, digest):
        """
        Send a digest for signing by the ECC

        :param digest: Digest to sign
        :return: Signature of signed digest
        """
        self.logger.info("ECC sign digest")
        return self.fwdriver.firmware_command("MC+ECC+SIGNDIGEST", [digest.hex()])

    def winc_read_fw_version(self):
        """
        Reads the FW version of the WINC module using provisioning FW

        :return: Firmware and driver version as a tuple
        """
        self.logger.debug("WINC read module FW version")
        response = self.fwdriver.firmware_command("MC+VERSION=WINC")
        # FW command returns FW version and driver version like this:
        # 'WINC firmware 19.6.5\nWINC driver 19.3.0'
        self.logger.debug(response)
        result = response.split()
        return (result[2], result[5])

    def winc_erase_tls_certificate_sector(self):
        """
        Erase TLS certificate sectors in WINC
        FIXME: this is redundant, remove?
        """
        self.logger.info("WINC erase TLS certificate sectors")
        for addr in range(FlashMap.tls_server_offset, FlashMap.tls_server_offset + FlashMap.tls_server_size,
                          FlashMap.sector_size):
            self.winc_erase_sector(addr)

    def winc_erase_sector(self, address):
        """
        Erase a WINC sector.

        :param address: Start adress of sector, must be a multiple of WINC_SECTOR_SIZE (4kB)
        """
        if address % FlashMap.sector_size:
            raise ValueError(f"Address 0x{address:x} is not sector aligned (0x{FlashMap.sector_size:x})")
        self.logger.info("WINC Erase sector at address 0x%06x", address)
        return self.fwdriver.firmware_command("MC+WINC+ERASE", [address])

    def winc_add_client_certificate(self, cert):
        """
        Add a client certificate to blob

        :param cert: Certifcate data (DER or PEM format)
        """
        self.tlsblob.add_certificate_blob(binascii.unhexlify(cert))

    def winc_write_tls_certificates_sector(self):
        """
        Create the WINC blob and write to target.
        """
        self.tlsblob.add_ecdsa_list()
        blob = self.tlsblob.build()
        self.winc_write(FlashMap.tls_server_offset, blob)

    def winc_write_thing_name(self, thing_name):
        """
        Write thing name to the WINC

        :param thing_name: Thing name to write
        :type thing_name: str
        """
        self.logger.debug("WINC write thing name")
        self.winc_write(FlashMap.thing_name_offset, thing_name.encode(self.encoding) + b'\0')

    def winc_write_endpoint_name(self, endpoint_name):
        """
        Write endpoint name to the WINC

        :param endpoint_name: Endpoint name to write
        :type endpoint_name: str
        """
        self.logger.debug("WINC write endpoint ")
        self.winc_write(FlashMap.aws_endpoint_offset, endpoint_name.encode(self.encoding) + b'\0')

    def winc_read(self, address, length):
        """
        Read data from WINC flash

        :param address: Start address to read from
        :type address: int
        :param length: Number of bytes to read
        :type length: int
        """
        self.logger.info("WINC read %d bytes from address 0x%x", length, address)
        result = b''
        for offset in range(0, length, FlashMap.page_size):
            page = binascii.unhexlify(self.fwdriver.firmware_command("MC+WINC+READ",
                                                                     [address + offset,
                                                                      min(FlashMap.page_size, length - offset)]))
            result += page
        return result

    def winc_write(self, address, data):
        """
        Write data to WINC flash

        :param address: Start address to write to
        :type address: int
        :param data: raw data to write
        :type data: encoded str
        """
        self.logger.info("WINC write %d bytes to address 0x%x", len(data), address)
        # Write one page at a time
        for offset in range(0, len(data), FlashMap.page_size):
            # Python kindly interprets end index out of range as -1
            page = data[offset : offset + FlashMap.page_size]
            self.logger.debug("WINC write page: offset 0x%04x size %3d, wincaddr=0x%06x", offset,
                              len(page), address + offset)
            status = self.fwdriver.firmware_command("MC+WINC+WRITEBLOB", [address + offset, len(page)],
                                                    binascii.hexlify(page))
            if status:
                raise PykitcommanderError("Write Winc failed: {}".format(status)) #FIXME more info
        return ""

    def read_fw_version(self):
        """
        Reads the FW version of the provisioning FW

        :return: Firmware version
        :rtype: str
        """
        self.logger.debug("Target read FW version")
        response = self.fwdriver.firmware_command("MC+VERSION=FIRMWARE")
        self.logger.debug("FW version: %s", response)
        return response

    def sw_reset(self):
        """
        Software Reset the provisioning firmware (using FW command)
        """
        self.logger.debug("Target FW software reset")
        try:
            return self.fwdriver.firmware_command("MC+RESET")
        except KitCommunicationError:
            # The fw_function might time out during the reset. But
            # after the device is reset an OK should be received
            return self.fwdriver.wait_for_reset()

    def reset(self):
        """
        Reset target via debugger. Wait for ready prompt from FW.
        """
        self.programmer.reset_target()
        return self.fwdriver.wait_for_reset()

    def enter_bridge_mode(self):
        """
        Enable bridge mode in target

        In bridge mode target will just forward data from the host to the modem UART and forward data from the modem
        UART to the host
        Note that when in bridge mode no normal commands will work

        :return: Empty string if OK
        :rtype: str
        :raises KitCommunicationError: If an unexpected response was received from target
        """
        self.logger.debug("Entering Bridge Mode")

        response = self.fwdriver.firmware_command("MC+BRIDGEMODE")
        if response:
            raise KitCommunicationError("Unexpected response from bridgeMode command: {}".format(response))
        return response

    def exit_bridge_mode(self):
        """
        Disable bridge mode in target

        :raises: KitCommunicationError: If an unexpected response was received from target
        """
        self.logger.debug("Leaving Bridge Mode")
        if self.com is None:
            raise PortError("Port not open.")
        self.com.read(self.com.in_waiting)     # Flush input buffer
        self.com.write(ASCII_EOT)
        response = self.com.read_until(b'\n').decode(self.encoding)
        # Note there might be some data still in the bridge mode pipe so the important part is the end of the data
        if response.endswith("OK\r\n"):
            return ""
        raise KitCommunicationError("Exit bridge mode failed, returned: '{}'".format(response))

    def _get_led_name(self, led_name):
        """
        Handle inconsistent naming of LEDS between Cellular and WiFi kits

        led_name could either be the name of the LED as written on the kits silkscreen print or the name according to
        the attributes of the pykitcommander.kitmanager.KitLeds class
        Example:
            - "WIFI", "CELL" and "WIRELESS_LED" all map to the same led, the CELL led on AVR-IoT Cellular or the WIFI
                led on PIC-/AVR-IoT wifi kits
        :param led_name: LED name passed from caller.
        :type led_name: str
        :return: correct LED name according to kit type
        """
        led_defs = self.kit_info['kit_info']['leds']
        actual_led_name = None
        if led_name.upper().startswith("ERR"):
            actual_led_name = led_defs.ERROR_LED
        elif led_name.upper() in ["WIFI", "CELL"] or led_name.upper().startswith("WIRELESS"):
            actual_led_name = led_defs.WIRELESS_LED
        elif led_name.upper().startswith("CONN"):
            actual_led_name = led_defs.CONNECTION_LED
        elif led_name.upper().startswith("DATA"):
            actual_led_name = led_defs.DATA_LED
        elif led_name.upper().startswith("USER"):
            actual_led_name = led_defs.USER_LED

        if not actual_led_name:
            raise PykitcommanderError(f"Unsupported LED: {led_name}")
        return actual_led_name

    def set_led_status(self, led, state):
        """
        Turn LED on or off

        :param led: Name of led to manipulate
        :type led: str
        :param state: "ON" or "OFF" (case-instensitve)
        :type state: str
        """
        return self.fwdriver.firmware_command("MC+SETLED", [self._get_led_name(led), state])

    def get_led_status(self, led):
        """
        Get LED state

        :param led: Name of led to check
        :type led: str
        :return: "ON" or "OFF"
        :rtype: str
        """
        return self.fwdriver.firmware_command("MC+GETLED", [self._get_led_name(led)])


class DemoFirmwareInterface(ApplicationFirmwareInterface):
    """
    Interface to demo firmware

    :param kit_info: Kit information from pykitcommander
    :type kit_info: dict
    :param programmer: Programmer to use
    :type programmer: object
    :param port: Serial port to connect to
    :type port: str, optional, defaults to the active kit
    :param stopbits: Number of stopbits to use
    :type stopbits: int, optional, defaults to 1
    :param encoding: Text encoding to use
    :type encoding: str, optional, defaults to UTF-8
    """
    DEFAULT_BAUD = 9600
    def __init__(self, kit_info, programmer, port=None, stopbits=1, encoding="UTF-8"):
        # FIXME: stopbits should come from kit_info
        super().__init__(kit_info, programmer, port=port, stopbits=stopbits, encoding=encoding)
        self.logger = getLogger(__name__)

    def open(self):
        """
        Open port, then send an initial empty command and discard the response (list of available commands).
        This reduces the risk of communication glitches on initial real command sent to demo FW.
        """
        super().open()
        _ = self.demo_fw_command("")

    # pylint: disable=dangerous-default-value
    def demo_fw_command(self, cmd, args=[]):
        """
        Send a request to demo FW CLI, return response.

        :param cmd: Command to send
        :type cmd: str
        :param args: arguments (payload)
        :type arge: list of str
        """
        if self.com is None:
            raise PortError("Port not open.")
        #TODO: refactor
        end_of_transmission = b'\\04'  # end of transmission from target
        buffer = ("{} {}\n").format(cmd, ",".join(args)).encode()
        sleep(0.1)     # Mystery delay between requests seems to avoid mixed-up responses
        # Experimental: Try to send a single character at a time to solve instability
        for c in buffer:
            buf = [c]
            self.com.write(buf)
            self.com.flush()
        response = self.com.read_until(end_of_transmission)[:-1].decode("utf-8", errors="ignore")
        return response

    def read_fw_version(self):
        """
        Get demo FW version.
        """
        # When called shortly after demo FW, there is considerable risk of garbled
        # communication, the first 3 lines below are to reduce that risk.
        # When called after demo FW programming or reset, demo FW will not respond until it
        # has started WiFi so will take a long while for it to respond in any case.
        sleep(3)
        self.com.flush()
        self.com.read(self.com.in_waiting)
        return self.demo_fw_command("version")
