#!/usr/bin/env python3
"""
This script can do one or more (default: all) of the following steps:

- Generate root and signer certificates, register with AWS (certs)
- Update the kit's debugger firmware to latest version
- Provision a connected IoT kit (provision)
- Program WINC AWS parameters needed by demo app
- Program kit with a demo/application (application)
- Optionally set up WiFi credentials in demo application

"""
# (see # https://confluence.microchip.com/display/XP/Provisioning+current+state+and+improvements)

import time
import argparse
import os
import sys
import logging
from logging.config import dictConfig
import yaml
from appdirs import user_log_dir
from yaml.scanner import ScannerError
from pytrustplatform.ca_create import DEFAULT_ORGANIZATION_NAME, DEFAULT_ROOT_COMMON_NAME, DEFAULT_SIGNER_COMMON_NAME

from .iotprovision_main import iotprovision, STATUS_SUCCESS, STATUS_FAILURE
from .provisioner import WIFI_AUTHS      #FIXME
from .cellular.cellularprovisioner import DEFAULT_CELLULAR_PROVIDER, CELLULAR_VALID_FREQ_BANDS
from .cellular.sequans_ciphersuites import DEFAULT_CIPHERSUITES, print_ciphersuites
from .deprecated import deprecated

# Supported cloud providers
CLOUD_PROVIDERS = ["google", "aws", "azure"]

ROOTCERTS_HELP = """
Action 'rootcerts' is used to manage root certificate storage in WINC flash.
It requires --install-root-certs or --restore-root-certs options:

  --irc ROOT_CERTS_FOLDER, --install-root-certs ROOT_CERTS_FOLDER
                        Install all certificate files in a folder in
                        WINC root certificate sector
  --rrc {backup,factory}, --restore-root-certs {backup,factory}
                        Restore WINC root certificates sector from backup or
                        factory defaults

When one of the above options are used, the previous root certificates sector
content will be saved to a backup file. Separate backup file is maintained
for each kit.

Usage examples:
  # Install all certificate files in 'my_certs_folder' in WINC root cert sector:
  iotprovision --install-root-certs my_certs_folder
  # Restore previous content of WINC certificates sector from backup:
  iotprovision --restore-root-certs backup
  # Restore WINC root certificates sector to factory defaults:
  iotprovision --restore-root-certs factory
"""

def setup_logging(user_requested_level=logging.WARNING, default_path='logging.yaml',
                  env_key='MICROCHIP_PYTHONTOOLS_CONFIG'):
    """
    Setup logging configuration for this CLI
    """
    # Logging config YAML file can be specified via environment variable
    value = os.getenv(env_key, None)
    if value:
        path = value
    else:
        # Otherwise use the one shipped with this application
        path = os.path.join(os.path.dirname(__file__), default_path)
    # Load the YAML if possible
    if os.path.exists(path):
        try:
            with open(path, 'rt') as file:
                # Load logging configfile from yaml
                configfile = yaml.safe_load(file)
                # File logging goes to user log directory under Microchip/modulename
                logdir = user_log_dir(__name__, "Microchip")
                # Look through all handlers, and prepend log directory to redirect all file loggers
                num_file_handlers = 0
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        configfile['handlers'][handler]['filename'] = os.path.join(
                            logdir, configfile['handlers'][handler]['filename'])
                        num_file_handlers += 1
                if num_file_handlers > 0:
                    # Create it if it does not exist
                    os.makedirs(logdir, exist_ok=True)

                if user_requested_level <= logging.DEBUG:
                    # Using a different handler for DEBUG level logging to be able to have a more detailed formatter
                    configfile['root']['handlers'].append('console_detailed')
                    # Remove the original console handlers
                    try:
                        configfile['root']['handlers'].remove('console_only_info')
                    except ValueError:
                        # The yaml file might have been customized and the console_only_info handler
                        # might already have been removed
                        pass
                    try:
                        configfile['root']['handlers'].remove('console_not_info')
                    except ValueError:
                        # The yaml file might have been customized and the console_only_info handler
                        # might already have been removed
                        pass
                else:
                    # Console logging takes granularity argument from CLI user
                    configfile['handlers']['console_only_info']['level'] = user_requested_level
                    configfile['handlers']['console_not_info']['level'] = user_requested_level

                # Root logger must be the most verbose of the ALL YAML configurations and the CLI user argument
                most_verbose_logging = min(user_requested_level, getattr(logging, configfile['root']['level']))
                for handler in configfile['handlers'].keys():
                    # A filename key
                    if 'filename' in configfile['handlers'][handler].keys():
                        level = getattr(logging, configfile['handlers'][handler]['level'])
                        most_verbose_logging = min(most_verbose_logging, level)
                configfile['root']['level'] = most_verbose_logging
            dictConfig(configfile)
            return
        except ScannerError:
            # Error while parsing YAML
            print("Error parsing logging config file '{}'".format(path))
        except KeyError as keyerror:
            # Error looking for custom fields in YAML
            print("Key {} not found in logging config file".format(keyerror))
    else:
        # Config specified by environment variable not found
        print("Unable to open logging config file '{}'".format(path))

    # If all else fails, revert to basic logging at specified level for this application
    print("Reverting to basic logging.")
    logging.basicConfig(level=user_requested_level)

def peek_cloudprovider():
    """
    Provide defaults help text for ciphersuites for specified cloud provider.
    """
    cloud = None
    for cloud in CLOUD_PROVIDERS:
        for arg in sys.argv:
            if ((arg.startswith("-c" or arg.startswith("--cloud"))) and arg.endswith(cloud)) or arg == cloud:
                return cloud
    return "aws"

def main():
    """
    Iotprovision main program. Parse out command-line arguments
    """
    # All possible actions. The [] at end is to allow no actions as default.
    # meaning ACTIONS_DEFAULT will be used. Argparse does not allow to specify multiple choices
    # (ACTIONS_DEFAULT) directly as default, and None doesn't work.
    ACTIONS_ALL = ["account", "debuggerupgrade", "wincupgrade", "rootcerts", "certs", "provision", "application", []]
    # Action(s) to be performed by default (ie if none are explicitly specified)
    ACTIONS_DEFAULT = ["account", "wincupgrade", "certs", "provision", "application"]

    ### The following is to help determine if cloud provider must be specified or not.
    # Provisioning actions needing cloud provider to be specified
    ACTIONS_NEEDING_CLOUDPROVIDER = ["account", "certs", "provision", "application"]
    # Options/arguments that will just print something and exit, not requiring cloud provider
    PRINT_ARGS = ["--help", "-h", "help", "-V", "--version", "-R", "--release-info"]

    parser = argparse.ArgumentParser(description="Provision an AVR-IoT, PIC-IoT or SAM-IoT kit for a cloud provider",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Action(s) to perform.
    parser.add_argument("actions", nargs="*", choices=ACTIONS_ALL,
                        help=f"Action(s) to perform, if none given, default is [{' '.join(ACTIONS_DEFAULT)}]")

    #Options for provisioning
    parser.add_argument(
        "-c", "--cloud-provider",
        # --cloud provider specification is required if:
        #  - Any command-line argument/option is given (else just print help and exit)
        #  - AND NOT any of the version/help options given (these print and exit immediately)
        #  - AND any of the real provisioning actions are specified explicitly
        #  -     OR no actions explictly specified (=> ACTIONS_DEFAULT will be used)
        required=(len(sys.argv) > 1
                  and not [arg for arg in sys.argv if arg in PRINT_ARGS]
                  and ([action for action in sys.argv if action in ACTIONS_NEEDING_CLOUDPROVIDER]
                       or not [action for action in sys.argv if action in ACTIONS_ALL])),
        help="Cloud provider to provision for",
        choices=CLOUD_PROVIDERS)

    parser.add_argument(
        "-m", "--provision-method",
        help="Provisioning method: Microchip sandbox, JITR or MAR (AWS custom account)",
        choices=["sandbox", "custom", "jitr", "mar"], default="sandbox")

    parser.add_argument(
        "-a", "--aws-profile",
        type=str, default="default",
        help="AWS profile name")

    parser.add_argument(
        "-P", "--port",
        type=str, default=None,
        help="Serial port name for communication with kit, only used when not successfully"
        " auto-detected")

    # Forcing options
    parser.add_argument(
        "--fca", "--force-ca-certs", action="store_true", dest="force_ca_certs",
        help="Force re-creation of CA certificates even if already existing")

    parser.add_argument(
        "--fdev", "--force-device-certs", action="store_true", dest="force_device_cert",
        help="Force re-creation of device and signer certificate even if already existing")

    parser.add_argument(
        "--faws", "--force-aws-cloudformation", action="store_true", dest="force_aws_cloudformation",
        help="Force re-creation of AWS cloudformation stack even if already existing")

    parser.add_argument(
        "--fwinc", "--force-wincupgrade", action="store_true", dest="force_wincupgrade",
        help="Force WINC upgrade even if not required for provisioning")

    parser.add_argument(
        "--sprov", "--skip-program-provision-firmware", action="store_true", dest="skip_program_provision_firmware",
        help="Skip programming provision firmware. NOTE: This is an advanced option and may break the process")

    # Options for creation of chain-of-trust (custom provisioning)
    parser.add_argument("--org", "--organization-name", type=str,
                        help="CA certificate issuer organization name",
                        required=False, default=DEFAULT_ORGANIZATION_NAME,
                        dest="organization_name")

    parser.add_argument("--rcn", "--root-common-name", type=str,
                        help="Root CA certificate issuer common name",
                        required=False, default=DEFAULT_ROOT_COMMON_NAME,
                        dest="root_common_name")

    parser.add_argument("--scn", "--signer-common-name", type=str,
                        help="Signer CA CSR common name",
                        required=False, default=DEFAULT_SIGNER_COMMON_NAME,
                        dest="signer_common_name")

    # Options to manage WINC root certificate storage, used with 'rootcerts' action
    # TODO: Should perhaps use this for cellular also, for HTTPS?
    rootcert_opts = parser.add_mutually_exclusive_group()
    rootcert_opts.add_argument("--irc", "--install-root-certs", type=str,
                        help="Install all certificate files in a folder in WINC root certificate storage",
                        dest="install_root_certs")

    rootcert_opts.add_argument("--rrc", "--restore-root-certs", choices=["backup", "factory"],
                        help="Restore WINC root certificates from backup or factory defaults",
                        dest="restore_root_certs")

    # WiFi setup options for demo application
    parser.add_argument(
        "--ssid", "--wifi-ssid", dest="wifi_ssid",
        type=str, help="SSID for wifi connection")

    parser.add_argument(
        "--psk", "--wifi-psk", dest="wifi_psk",
        type=str, default="", help="PSK (password) for wifi connection")

    parser.add_argument(
        "--auth", "--wifi-auth", dest="wifi_auth",
        default="wpa-psk", choices=WIFI_AUTHS.keys(),
        help="wifi authentication mechanism")

    # Cellular options. Cellular kit is auto-detected in provisioner.
    # All Cellular-only options should have a long option name STARTING WITH
    # "--cellular-" to be able to warn about incorrect use (if the selected board
    # is not a Cellular kit)
    # TODO: Should there be an option to force Cellular provisioning even when not auto-detected?
    #parser.add_argument(
    #    "--fcellular", "--cellular-force", action="store_true", dest="cellular_force",
    #    help="Force Cellular provisioning even when Cellular kit not auto-detected")

    # As of now, we don't support any cellular specific options.


    # Misc options
    parser.add_argument("-s", "--serialnumber", type=str,
                        help="USB serial number of the unit to provision")

    parser.add_argument("--verify", help="verify after write from file", action="store_true")

    parser.add_argument("-v", "--verbose",
                        default="info",
                        choices=['debug', 'info', 'warning', 'error', 'critical'],
                        help="Logging verbosity/severity level")

    parser.add_argument("-V", "--version", action="store_true",
                        help="Print iotprovision version number and exit")

    parser.add_argument("-R", "--release-info", action="store_true",
                        help="Print iotprovision release details and exit")

    args = parser.parse_args()

    # If no actions were specified, use default set
    if not args.actions:
        args.actions = ACTIONS_DEFAULT

    # Additional args not part of CLI invocation syntax (start with '_' to avoid name conflict)
    args._installdir = os.path.abspath(os.path.dirname(__file__))

    # Setup logging
    setup_logging(user_requested_level=getattr(logging, args.verbose.upper()))

    # If no arguments are provided - show help, pause and exit
    # Do this outside of argparse wrapper for simplicity
    if len(sys.argv) <= 1:
        # Display help text
        parser.print_help()
        print("\niotprovision must be executed from the command line with one or more arguments!")
        # Delay to allow novice users executing this utility to see that they are calling a CLI
        time.sleep(3)
        return 1

    # Handle version options here because we will exit immediately after
    if args.version or args.release_info:
        return print_version_info(args)

    if "rootcerts" in args.actions:
        if not (args.install_root_certs or args.restore_root_certs):
            print(ROOTCERTS_HELP)
            return STATUS_FAILURE
    elif args.install_root_certs or args.restore_root_certs:
        print("Options '--irc/--install-root-certs' and '--rrc/--restore-root-certs' only used with 'rootcerts' action")
        return STATUS_FAILURE

    # Deprecated stuff
    args = deprecated(args)
    if not args:
        return "Internal error handling deprecations"

    return iotprovision(args)

def print_version_info(args):
    """
    Print version and related info from version.py
    Existence of version.py requires wheel is built
    """
    try:
        from . import version
        print("{} version {}".format(os.path.basename(sys.argv[0]), version.VERSION))
        if args.release_info:
            print("Build date:  {}".format(version.BUILD_DATE))
            print("Commit ID:   {}".format(version.COMMIT_ID))
            print("Installed in {}".format(args._installdir))
        return STATUS_SUCCESS
    except Exception as e:
        return "Could not retrieve version: {}".format(e)


if __name__ == '__main__':
    sys.exit(main())
