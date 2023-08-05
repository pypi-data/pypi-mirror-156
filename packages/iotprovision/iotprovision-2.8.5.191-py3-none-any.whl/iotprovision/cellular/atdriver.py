"""
Simple driver for Monarch GO AT modemcontrol commands
"""

from time import sleep
from logging import getLogger
from ..provisioner import ProvisionerError

ASCII_EOT = b'\x04'


class AtDriver():
    """
    Low-level AT modem command driver.
    """

    def __init__(self, fwinterface):
        """
        Connstructor. Will enter bridge mode. Protocol port must be opened by caller.

        :param fwinterface: Firmware interface object
        """
        self.logger = getLogger(__name__)
        self.bridge_mode = False
        self.fwinterface = fwinterface
        self.com = self.fwinterface.get_comport_handle()
        self.enter_bridge_mode()

    def __del__(self):
        self.exit_bridge_mode()

    def __enter__(self):
        self.enter_bridge_mode()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.exit_bridge_mode()

    def enter_bridge_mode(self):
        """
        Need to manage bridge state internally because pykitcommanader doesn't yet.
        """
        self.logger.debug("enter_bridge_mode")
        if self.bridge_mode:
            self.logger.debug("Already in bridge mode")
            return
        # The blue LED used to indicate bridge mode (ie we're talking to the modem)
        self.fwinterface.set_led_status("CELL", "ON")
        response = self.fwinterface.enter_bridge_mode()
        if response == "":
            self.bridge_mode = True
            # Wait for modem being ready after reset
            self.read_until(b"+SYSSTART", retries=2, timeout=1)
            # Flush any garbage the modem might still have in store
            garbage = self.com.read(self.com.in_waiting)
            if garbage:
                self.logger.debug("Garbage from modem: %s", garbage)
            self.ping()                         # Sanity check - this should not fail
        else:
            self.fwinterface.set_led_status("ERR", "ON")
            raise ProvisionerError("Enter bridge mode failed, response: {}".format(response))

    def exit_bridge_mode(self):
        """
        Exit bridge mode.
        """
        self.logger.debug("exit_bridge_mode")
        if not self.bridge_mode:
            self.logger.debug("Already out of bridge mode")
            return
        response = self.fwinterface.exit_bridge_mode()
        if response == "":
            sleep(.3)                              # Wait for any garbage chars after switching mode
            self.bridge_mode = False
            self.fwinterface.set_led_status("CELL", "OFF")
        else:
            self.fwinterface.set_led_status("ERR", "ON")
            raise ProvisionerError("Exit bridge mode failed, response: {}".format(response))

    def ping(self):
        """
        Send 'AT' command to modem and check response

        :return: True if modem responds "OK"
        """
        if self.bridge_mode:
            response = self.command("AT")
            if response[-1] == "OK":
                return True
            raise ProvisionerError("Modem ping failed, response: {}".format(response))
        raise ProvisionerError("Modem ping attempted when not in bridge mode")

    def read_response(self):
        """
        Read response from modem. Response can be multiple lines either
        ended with "OK\\r\\n", "ERROR\\r\\n", or '>' so a simple read_until
        won't do. Returns list of response lines, blank lines and
        CR-LF stripped.
        """
        lines = []
        while True:
            line = self.com.read_until(b'\r\n')
            if not line:
                lines.append("ERROR: Timeout")
                return lines
            if line != b'\r\n':
                lines.append(line[0:-2].decode("utf-8", "ignore"))
                if line[0:2] == b"OK" or b"ERROR" in line:
                    return lines

    def read_until(self, string, expect=b'\r\n', retries=1, timeout=None):
        """
        Read complete lines until a line containing string is read.
        Can be used to wait for expected URCs after a given command.

        :param string: string to wait for
        :param expect: Optional character to read until if not whole line read
        :param retries: Number of times to retry after timeout waiting for string before giving up
        :return: list of response lines.
        """
        # TODO: extend to do regular expression matching.
        lines = []
        tm = self.com.timeout
        if timeout:
            self.com.timeout = timeout
        while True:
            line = self.com.read_until(expect)
            if not line:
                # For situations where the comm timeout is not enough.
                retries -= 1
                if retries > 0:
                    continue
                lines.append("ERROR: Timeout")
                self.com.timeout = tm
                return lines
            if line != b'\r\n':   # Strip blank lines
                if line.endswith(b'\r\n'):
                    lines.append(line[0:-2].decode("utf-8", "ignore"))
                else:
                    lines.append(line.decode("utf-8", "ignore"))
                if string in line:
                    self.com.timeout = tm
                    return lines

    def command(self, cmd, payload=None):
        """
        Send simple AT command.

        :param cmd: Pre-formatted command.
        :param payload: Optional payload sent in separate line. Payload length is appended
            as argument to cmd. Payload == "" will append payload length argument while None will not.
            (used for erase in AT+SQNSNVW command)
        :return: sanitized response (list of lines) Last line will be "OK" or "ERROR"
        """
        if payload is None:
            self.logger.debug(cmd)
            self.com.write((cmd + '\r').encode())
        else:
            self.logger.debug("%s,%d", cmd, len(payload))
            self.com.write((cmd + ",{}\r".format(len(payload))).encode())
            if len(payload) > 0:
                self.com.read_until(b'>')
                self.com.write(payload)
        response = self.read_response()
        self.logger.debug(response)
        return response

    def write_nvm(self, datatype, slot, data=None, cmd="AT+SQNSNVW"):
        """
        Write data to NVM. Requires special handling because Sequans modem requires
        certificate PEM files use '\\n' line endings and line ending not missing on last line.

        :param cmd:  "AT+SQNSNVW" (maybe others as well?)
        :param datatype: "certificate", "privatekey", or "strid" (don't know what the latter is used for)
        :param slot: 0-19, 0-5 for "strid"
        :param data: data to write. None/empty => erase slot.
        """
        if not datatype in ["certificate", "privatekey"]:
            raise ValueError(f"Invalid data type for NVM write: {datatype}")

        if data:
            data = data.replace(b'\r\n', b'\n')  # Get rid of CR-LF line endings if present
            # Sequans modem requires PEM input ends with newline
            if not data.endswith(b'\n'):
                self.logger.warning("missing newline at end of data, appending")
                data += b'\n'
        else:
            data = b''

        response = self.command(cmd + f'="{datatype}",{slot}', data)
        if response[-1] != "OK":
            raise ProvisionerError(f"Write {datatype} to NVM failed, response: {response}")

    def reset(self):
        """
        Software-reset modem, wait for startup to complete
        """
        response = self.command("AT^RESET")
        if response[-1] == "OK":
            self.read_until(b'+SYSSTART')
            return
        raise ProvisionerError("Reset modem failed")
