"""
Top-level logic of IOT provisioning program
"""

import os
from logging import getLogger
from packaging import version
from pykitcommander.kitmanager import KitProgrammer
from pykitcommander.kitcommandererrors import KitConnectionError, KitCommunicationError, PykitcommanderError
from .provisioner import get_provisioner, ProvisionerError
from .cellular.cellularprovisioner import get_cellular_provisioner
from .config import Config
from .winc_root_certs import WincRootCerts

STATUS_SUCCESS = 0
STATUS_FAILURE = 1

logger = getLogger(__name__)

def iscellular(kit_name):
    """
    Determine if a kit is a cellular kit or a WiFi kit based on kit name.
    :param kit_name: Name of the kit
    the LTE-M name is only used in prototype kits
    """
    return "CELLULAR" in kit_name.upper() or "LTE-M" in kit_name


def iotprovision(args):
    """
    iotprovision executioner
    :param args: Parsed-out command line arguments
    :return: Exit code (0 == success)
    """

    # CLI + binary has info logging by default, so we can use that for a welcome message
    logger.info("***** AVR-IoT, PIC-IoT and SAM-IoT provisioning utility 'iotprovision' *****")
    provisioner = None
    status = STATUS_SUCCESS
    try:
        try:
            programmer = KitProgrammer(args.serialnumber)
            kit_name = programmer.get_kit_info().get("kit_name")
            tool = programmer.get_kit_info().get("programmer_id")
            serialnumber = programmer.get_kit_info().get("serialnumber")

            # Give user some details about the process
            if args.cloud_provider:
                logger.info("Start processing '%s' kit for use with %s %s",
                            kit_name, args.cloud_provider,
                            args.provision_method if args.cloud_provider == "aws" else "")

            # Create certificates folder if it does not exist.
            os.makedirs(os.path.join(Config.Certs.certs_dir, serialnumber), exist_ok=True)

            # Look up the provisioner helper. Different subclasses for WiFi and Cellular kits.
            if iscellular(kit_name):
                provisioner = get_cellular_provisioner(programmer, args)
                # CellularProvisioner needs some extra parameters
                provisioner.set_cellular_params(args)
            else:
                provisioner = get_provisioner(programmer, args)
        except KitConnectionError as e:
            print_kit_status(e)
            return STATUS_FAILURE

        if "account" in args.actions:
            if args.cloud_provider == "aws":
                logger.info("\nSet up '%s' account", args.cloud_provider)
                provisioner.setup_account(args.aws_profile, args.force_aws_cloudformation)
            else:
                # Account setup for azure and google are not part of this process
                logger.debug("\nSkipping account setup for '%s' (not required)", args.cloud_provider)

        # If user specifies debugger upgrade, do so if bundled version is newer than current,
        # otherwise only upgrade if current is older than absolute minimum required version
        debugger_version = provisioner.get_debugger_version()
        if "debuggerupgrade" in args.actions or \
           version.parse(debugger_version) < version.parse(provisioner.MINIMUM_DEBUGGER_VERSION):
            logger.info("\nCheck if debugger firmware (%s) needs upgrade...", debugger_version)
            logger.debug("Current debugger version is: %s, absolute minimum required is %s",
                         debugger_version, provisioner.MINIMUM_DEBUGGER_VERSION)
            provisioner.debuggerupgrade(tool)

        if "wincupgrade" in args.actions:
            if iscellular(kit_name):
                logger.info("%s kit has no WINC, skipping", kit_name)
            else:
                logger.info("\nCheck if WINC firmware needs upgrade...")
                provisioner.winc_upgrade(args.force_wincupgrade)

        if "rootcerts" in args.actions:
            if iscellular(kit_name):
                logger.error("\n%s kit has no WINC, leaving", kit_name)
                return STATUS_FAILURE

            if args.install_root_certs and not os.listdir(args.install_root_certs):
                logger.error("Root certificate folder '%s' is empty", args.install_root_certs)
                return STATUS_FAILURE

            provisioner.connect("iotprovision", args.skip_program_provision_firmware)
            manage_root_certs(provisioner.fwinterface, args, serialnumber)

        if "certs" in args.actions:
            logger.info("\nGenerate certificates if required...")
            provisioner.generate_certificates(force=args.force_ca_certs,
                                              organization_name=args.organization_name,
                                              root_common_name=args.root_common_name,
                                              signer_common_name=args.signer_common_name)

        if "provision" in args.actions:
            logger.info("\nProvisioning %s for %s %s...",
                        kit_name, args.cloud_provider,
                        args.provision_method if args.cloud_provider == "aws" else "")

            provisioner.do_provision(force_new_device_certificate=args.force_device_cert,
                                     skip_program_provision_firmware=args.skip_program_provision_firmware)

        if "application" in args.actions:
            logger.info("\nProgramming application: %s...",
                        "Bundled Demo for {}".format(args.cloud_provider))
            provisioner.program_application(args.cloud_provider)

        if args.wifi_ssid and not iscellular(kit_name):
            logger.info("\nSetting up WiFi credentials...")
            provisioner.setup_wifi(cloud_provider=args.cloud_provider,
                                   ssid=args.wifi_ssid,
                                   psk=args.wifi_psk,
                                   auth=args.wifi_auth)

    except ProvisionerError as e:
        logger.error("Operation failed with %s: %s", type(e).__name__, e)
        logger.debug(e, exc_info=True)    # get traceback if debug loglevel
        status = STATUS_FAILURE

    except PykitcommanderError as e:
        # Pykitcommander exceptions carry useful info in attribute 'msg' which other
        # exceptions don't have.
        logger.error("Operation failed with %s: %s", type(e).__name__, e.msg)
        logger.debug(e, exc_info=True)    # get traceback if debug loglevel
        status = STATUS_FAILURE

    except SystemExit as e:
        # Should never happen: Exit directly from library code we use.
        logger.error("Premature exit, %s: %s", type(e).__name__, e)
        logger.debug(e, exc_info=True)                # get traceback if debug loglevel
        status = e.code if e.code else STATUS_FAILURE # Use actual exit code unless it is zero.

    except Exception as e:
        logger.error("Operation failed with %s: %s", type(e).__name__, e)
        logger.debug(e, exc_info=True)    # get traceback if debug loglevel
        status = STATUS_FAILURE

    if status == STATUS_SUCCESS:
        if provisioner and provisioner.debugger_reboot_required:
            # This must always be done last, so do it here.
            # It could be done in provisioner.__del__(), but python destructors
            # are not guaranteed to be called.
            logger.info("Rebooting debugger...")
            provisioner.reboot_debugger()

        logger.info("Operation completed successfully.")

    return status


def print_kit_status(error):
    """
    Print details from KitConnectionError exception due to none or too many kits
    matching serial number specification (if any)

    :param error: KitConnectionError exception object
    """
    # There must be exactly one tool connected, or user must disambiguate with (partial)
    # serial number
    logger = getLogger(__name__)
    if not error.value:
        logger.error("Provisioning unable to start - no suitable IoT kits found")
    elif len(error.value) > 1:
        logger.error("Provisioning unable to start - multiple kits found.")
        logger.error("Please specify serial number ending digits for the one you want")
        for tool in error.value:
            logger.error("Tool: %s Serial: %s Device: %s",
                         tool["product"][:16],
                         tool["serial"][:20],
                         tool["device_name"])
        # Should we offer interactive selection here?
    else:
        # If exactly one was found, something is wrong with it, expect reason in msg
        tool = error.value[0]
        logger.error("Provisioning unable to start - Tool: %s Serial: %s Device: %s: %s",
                     tool["product"][:16],
                     tool["serial"][:20],
                     tool["device_name"],
                     error.msg)


def manage_root_certs(fwinterface, args, serialnumber):
    """
    Manage the WINC root certificate sector operations.
    """
    backupfile = Config.Certs.get_path("root_certs_backup_file", serialnumber)
    factoryfile = os.path.join(args._installdir, "fw", "winc", "tls_root_cert.bin")

    with WincRootCerts(fwinterface, backupfile, factoryfile) as rootcerts:
        if args.install_root_certs:
            logger.info("\nInstall WINC root certificates from folder '%s'",
                        args.install_root_certs)
            # Expand folder to a list of files in the folder
            files = sorted(
                [os.path.join(args.install_root_certs, file)
                 for file in os.listdir(args.install_root_certs)
                 if os.path.isfile(os.path.join(args.install_root_certs, file))],
                key=str.lower)
            rootcerts.write_rootcerts_blob(rootcerts.build_rootcerts_blob(files))
        elif args.restore_root_certs == "backup":
            logger.info("\nRestore WINC root certificates from backup")
            rootcerts.write_rootcerts_file(backupfile)
        elif args.restore_root_certs == "factory":
            logger.info("\nRestore WINC root certificates to factory defaults")
            rootcerts.write_rootcerts_file(factoryfile)
        else:
            raise ValueError(f"Invalid root certificates restore source: {args.restore_root_certs}")
