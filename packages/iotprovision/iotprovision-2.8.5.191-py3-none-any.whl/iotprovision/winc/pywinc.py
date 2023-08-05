#!/usr/bin/env python3
"""
This module handles the WINC FW and certificate upgrade.

Features:
- Update the WINC FW
- Build root certificate storage and upgrade WINC with it
- Build client file storage and upgrade WINC with it
- Read root certificate storage from WINC
- Read client file storage from WINC
"""
import sys
import argparse
import textwrap
import logging
from pykitcommander.kitmanager import KitConnectionError
from . import pywinc_main
from ..iotprovision import setup_logging
from ..iotprovision_main import print_kit_status


def main():
    """
    Entrypoint for installable CLI

    Configures the CLI and parses the arguments
    """
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''\
    WINC FW upgrade and certificates update tool

    Basic actions:
        - read: read a storage object from WINC flash
        - write: write a storage object to WINC flash
        - build: build a storage object
        - decode: decode a storage object
        - fwupgrade: upgrade WINC FW
            '''),
                                     epilog=textwrap.dedent('''\
    Usage examples:

        Read WINC root certificate storage and save to root-certs.bin:
        - pywinc read -m root-certs -o root-certs.bin

        Read WINC client certificate storage and save to client-certs.bin:
        - pywinc read -m client-certs -o client-certs.bin

        Build a WINC root certificate storage object from certificates in a directory
        - pywinc build -m root-certs -i directory-with-root-certs -o root-certs.bin

        Build a WINC root certificate storage object from a list of certificates
        - pywinc build -m root-certs -i cert1.cer cert2.cer cert3.cer -o root-certs.bin

        Build a WINC client certificate storage object from a list of certificates
        - pywinc build -m client-certs -i device.cer signer.cer -o client-certs.bin

        Write root certificate storage in WINC flash:
        - pywinc write -m root-certs -i root_certs.bin

        Write client certificate storage in WINC flash:
        - pywinc write -m client-certs -i client_certs.bin

        Decode a root certificate storage object:
        - pywinc decode -m root-certs -i root_certs.bin

        Decode a client certificate storage object:
        - pywinc decode -m client-certs -i client_certs.bin

        Upgrade WINC FW:
        - pywinc fwupgrade -i winc_fw.bin
        '''))

    parser.add_argument("action", help="Actions to perform",
                        nargs="?" if "-V" in sys.argv or "--version" in sys.argv else None,
		        choices=['read', 'write', 'build', 'decode', 'fwupgrade'])

    parser.add_argument("-p", "--port",
                        type=str,
                        help="Optional serial port to use for reading out the certificate store e.g. COM5.\
                        Auto-detected if not provided")

    parser.add_argument("-s", "--serialnumber", type=str,
                        help="USB serial number of unit to connect to")

    parser.add_argument("--skip", "--skip-target-programming", dest="skip_target_programming",
                        help="Skip programming WINC upgrade firmware", action="store_true")

    parser.add_argument("-m", "--memory",
                        type=str,
                        choices=['root-certs', 'client-certs'],
                        required=any(action in sys.argv for action in ['read', 'write', 'build', 'decode']),
                        help="Memory to perform the action on. Valid memory types: root-certs, client-certs")

    parser.add_argument("-i", "--input",
                        nargs='+',
                        required=any(action in sys.argv for action in ['build', 'write', 'decode', 'fwupgrade']),
                        help="Input file, list of input files or a directory.")

    parser.add_argument("-o", "--out",
                        type=str,
                        default=None,
                        help="File where to store the certificate storage object")

    parser.add_argument("-d", "--decode",
                        action="store_true",
                        help="Decode and print the certificate store to stdout")

    parser.add_argument("-v", "--verbose",
                        help="Logging verbosity/severity level",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        default="info")

    parser.add_argument("-V", "--version",
                        help="Print version number and exit",
                        action="store_true")
    args = parser.parse_args()

    logging_level = getattr(logging, args.verbose.upper())
    setup_logging(user_requested_level=logging_level)

    try:
        return pywinc_main.pywinc(args, logging_level)
    except KitConnectionError as e:
        print_kit_status(e)
        return pywinc_main.STATUS_ERROR
    # TODO: handle other relevant exceptions also

if __name__ == "__main__":
    sys.exit(main())
