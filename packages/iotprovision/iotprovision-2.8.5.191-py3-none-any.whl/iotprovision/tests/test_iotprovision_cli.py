# The intention is to make the test names descriptive enough to not need any docstrings for most of them
#pylint: disable=missing-docstring
"""
Tests for the iotprovision CLI
"""
import sys
import io
import os
import shutil
import unittest
import logging
from copy import copy

from mock import patch, MagicMock
import mock

from pykitcommander.kitcommandererrors import KitConnectionError, KitCommunicationError

from iotprovision.iotprovision import main
from iotprovision.version import VERSION
from iotprovision.provisioner import Provisioner
from iotprovision.config import Config

TEST_LOG_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp', "test_cli_log_files")
TEST_CERT_ROOT_FOLDER = "test_iotprovision_cli_files"
NEDBG_FW = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fw", "nedbg_fw.zip"))

DEFAULT_KIT_INFO = {
    "device_name": "atmega4808",
    "product": "nedbg",
    "serialnumber": "MCHP0123456789",
    "kit_name": "Test AVR-IoT",
    "port": "PORTX",
    "programmer_id": "nedbg",
    "protocol_id": "ProvisioningV2"
}

STATUS_SUCCESS = 0
STATUS_FAILURE = 1

class TestIotprovisionCli(unittest.TestCase):
    """
    Integration tests for the iotprovision CLI
    """
    def setUp(self):
        # Modify log folder to avoid permission denied problems when running on Jenkins as the original
        # log folder location will be outside the workspace of the build job
        self.mock_user_log_dir_patch = patch('iotprovision.iotprovision.user_log_dir')
        self.addCleanup(self.mock_user_log_dir_patch.stop)
        self.mock_user_log_dir = self.mock_user_log_dir_patch.start()
        self.mock_user_log_dir.return_value = TEST_LOG_FOLDER

    def mock_provisioneraws(self):
        """
        Mock out the ProvisionerAws instance of iotprovision.provisioner

        This will mock out the ProvisionerAws instance returned by get_provisioner()
        """
        mock_provisioneraws_patch = patch("iotprovision.provisioner.ProvisionerAws")
        self.addCleanup(mock_provisioneraws_patch.stop)
        mock_provisioneraws = mock_provisioneraws_patch.start()
        # Fetch the return value of the ProvisionerAws mock
        mock_provisioneraws_inst = mock_provisioneraws.return_value
        # Just pretent everything went well with the provisioning
        mock_provisioneraws_inst.MINIMUM_DEBUGGER_VERSION = "1.15.479"
        mock_provisioneraws_inst.get_debugger_version.return_value = "1.22.73"
        mock_provisioneraws_inst.setup_account.return_value = STATUS_SUCCESS
        mock_provisioneraws_inst.debuggerupgrade.return_value = STATUS_SUCCESS
        mock_provisioneraws_inst.winc_upgrade.return_value = STATUS_SUCCESS
        mock_provisioneraws_inst.generate_certificates.return_value = STATUS_SUCCESS
        mock_provisioneraws_inst.program_application.return_value = STATUS_SUCCESS
        mock_provisioneraws_inst.do_provision.return_value = STATUS_SUCCESS

        return mock_provisioneraws_inst

    def _mock_pydebuggerupgrade_backend_obj(self, update_fw_version):
        """
        Mock out the Backend instance of the Provisioner class

        The mock will report current firmware version, update firmware version and hex file name according to provided
        parameters
        :param update_fw_version: Version of firmware upgrade candidate
        :return: a mock of the Backend object of the pydebuggerupgrade module
        """
        mock_pydebuggerupgrade_backend_patch = patch("iotprovision.provisioner.Backend", autospec=True)
        self.addCleanup(mock_pydebuggerupgrade_backend_patch.stop)
        # Create mock of the pydebuggerupgrade Backend class
        mock_pydebuggerupgrade_backend = mock_pydebuggerupgrade_backend_patch.start()
        # Fetch the mock that will be returned when someone attempts to instantiate a Backend object
        mock_pydebuggerupgrade_backend_obj = mock_pydebuggerupgrade_backend.return_value

        mock_pydebuggerupgrade_backend_obj.upgrade_from_source.return_value = (True, update_fw_version)
        return mock_pydebuggerupgrade_backend_obj

    def _mock_stdout(self):
        """
        Returns stdout mock.

        Content sent to stdout can be fetched with mock_stdout.getvalue()
        """
        mock_stdout_patch = patch('sys.stdout', new_callable=io.StringIO)
        self.addCleanup(mock_stdout_patch.stop)
        return mock_stdout_patch.start()

    def _mock_stderr(self):
        """
        Returns stderr mock.

        Content sent to stderr can be fetched with mock_stderr.getvalue()
        """
        mock_stderr_patch = patch('sys.stderr', new_callable=io.StringIO)
        self.addCleanup(mock_stderr_patch.stop)
        return mock_stderr_patch.start()

    def _mock_kitprogrammer_obj(self, kit_info):
        """
        Mock out the KitProgrammer instance of iotprovision

        :param kit_info: kit info dict to be applied to the KitProgrammer object mock
        :type kit_info: dict
        """
        mock_kitprogrammer_patch = patch("iotprovision.iotprovision_main.KitProgrammer")
        self.addCleanup(mock_kitprogrammer_patch.stop)
        # Create mock of the Provisioner KitProgrammer class
        mock_kitprogrammer = mock_kitprogrammer_patch.start()
        # Fetch the mock that will be returned when someone attempts to instantiate a KitProgrammer object
        mock_kitprogrammer_obj = mock_kitprogrammer.return_value
        mock_kitprogrammer_obj.kit_info = kit_info
        return mock_kitprogrammer_obj

    def _mock_provisioningfirmwareinterface_obj(self):
        """
        Mock out the ProvisioningFirmwareInterface instance of the Provisioner class
        """
        mock_provisioningfirmwareinterface_patch = patch("iotprovision.provisioner.ProvisioningFirmwareInterface")
        self.addCleanup(mock_provisioningfirmwareinterface_patch.stop)
        mock_provisioningfirmwareinterface = mock_provisioningfirmwareinterface_patch.start()
        # Fetch the mock that will be returned when someone attempts
        # to instantiate a ProvisioningFirmwareInterface object
        mock_provisioningfirmwareinterface_obj = mock_provisioningfirmwareinterface.return_value
        return mock_provisioningfirmwareinterface_obj

    def _mock_winc_upgrade(self):
        mock_winc_upgrade_patch = patch("iotprovision.provisioner.Provisioner.winc_upgrade")
        self.addCleanup(mock_winc_upgrade_patch.stop)
        mock_winc_upgrade = mock_winc_upgrade_patch.start()
        # Just pretend the winc_upgrade is always successful
        mock_winc_upgrade.return_value = 0
        return mock_winc_upgrade

    def _mock_setup_kit(self):
        mock_setup_kit_patch = patch("iotprovision.provisioner.setup_kit")
        self.addCleanup(mock_setup_kit_patch.stop)
        mock_setup_kit = mock_setup_kit_patch.start()

        return mock_setup_kit

    @staticmethod
    def _remove_folder(folder):
        """
        Remove the specified folder and all it's content

        This function is useful to add to the test cleanup, self.addCleanup(self._remove_folder, folder)
        """
        # Remove certificate folder
        try:
            shutil.rmtree(folder)
        except FileNotFoundError:
            # Folder is already gone
            pass

    def test_get_version(self):
        mock_stdout = self._mock_stdout()
        testargs = ["iotprovision", "--version"]
        with patch.object(sys, 'argv', testargs):
            retval = main()
        self.assertEqual(retval, 0)
        self.assertTrue('iotprovision version {}'.format(VERSION) in mock_stdout.getvalue())

    def test_get_help(self):
        mock_stdout = self._mock_stdout()
        testargs = ["iotprovision", "--help"]
        with patch.object(sys, 'argv', testargs):
            # The --help argument is a built-in part of argparse so it will result in a SystemExit exception instead of
            #  a normal return code
            with self.assertRaises(SystemExit) as system_exit:
                main()
        self.assertEqual(system_exit.exception.code, 0)
        self.assertTrue('usage: iotprovision' in mock_stdout.getvalue())

    def test_not_connected(self):
        mock_stdout = self._mock_stdout()
        # Mock KitProgrammer class
        mock_kitprogrammer_patch = patch("iotprovision.iotprovision_main.KitProgrammer")
        # Create mock of the Provisioner KitProgrammer class
        mock_kitprogrammer = mock_kitprogrammer_patch.start()
        # When no kit is connected a KitConnectionError is raised
        mock_kitprogrammer.side_effect = KitConnectionError(msg="Exception injected by KitProgrammer mock", value=[])

        testargs = ["iotprovision", "-caws"]
        with patch.object(sys, 'argv', testargs):
            retval = main()
        self.assertEqual(retval, 1)
        self.assertTrue('no suitable IoT kits found' in mock_stdout.getvalue(), msg=mock_stdout.getvalue())

    def test_too_many_connected(self):
        tool_info = {
            "device_name": "atmega4808",
            "serial": "MCHP0123456789",
            "product": "nedbg"
        }

        # Mock KitProgrammer class
        mock_kitprogrammer_patch = patch("iotprovision.iotprovision_main.KitProgrammer")
        # Create mock of the Provisioner KitProgrammer class
        mock_kitprogrammer = mock_kitprogrammer_patch.start()

        # This mock just throws exceptions
        mock_kitprogrammer.side_effect = KitConnectionError(msg="Exception injected by KitProgrammer mock", value=[tool_info, tool_info])
        mock_stdout = self._mock_stdout()

        testargs = ["iotprovision", "-caws"]
        with patch.object(sys, 'argv', testargs):
            retval = main()
        self.assertEqual(retval, 1)
        self.assertTrue('multiple kits found' in mock_stdout.getvalue(), msg=mock_stdout.getvalue())

    def test_iotprovision_action_avr(self):
        """
        Testing basic iotprovision action without any extra parameters

        Mocking out all external dependencies, pretending one kit is connected and everything executes without failure
        """
        kit_info = copy(DEFAULT_KIT_INFO)

        self._mock_kitprogrammer_obj(kit_info)
        self.mock_provisioneraws()

        # Modify certificate folder to avoid permission denied problems when running on Jenkins as the original
        # certificate folder location will be outside the workspace of the build job
        certs_folder = os.path.join(TEST_CERT_ROOT_FOLDER, ".microchip-iot", kit_info["serialnumber"])
        Config.Certs.certs_dir = certs_folder

        # Make sure the certificate folder gets deleted even if the test fails
        self.addCleanup(self._remove_folder, TEST_CERT_ROOT_FOLDER)

        # Run the code to be tested
        testargs = ["iotprovision", "-caws"]
        with patch.object(sys, "argv", testargs):
            status = main()

        # Check that the code executed as expected
        self.assertEqual(status, 0, msg="Command failed (main() returned: {})".format(status))

    def test_iotprovision_action_pic(self):
        """
        Testing basic iotprovision action without any extra parameters

        Mocking out all external dependencies, pretending one kit is connected and everything executes without failure
        """
        self.mock_provisioneraws()

        kit_info = copy(DEFAULT_KIT_INFO)
        kit_info["device_name"] = "pic24fj128ga705"
        kit_info["kit_name"] = "Test PIC-IoT"

        self._mock_kitprogrammer_obj(kit_info)

        # Modify certificate folder to avoid permission denied problems when running on Jenkins as the original
        # certificate folder location will be outside the workspace of the build job
        certs_folder = os.path.join(TEST_CERT_ROOT_FOLDER, ".microchip-iot", kit_info["serialnumber"])
        Config.Certs.certs_dir = certs_folder

        # Make sure the certificate folder gets deleted even if the test fails
        self.addCleanup(self._remove_folder, TEST_CERT_ROOT_FOLDER)

        # Run the code to be tested
        testargs = ["iotprovision", "-caws"]
        with patch.object(sys, "argv", testargs):
            status = main()

        # Check that the code executed as expected
        self.assertEqual(status, 0, msg="Command failed (main() returned: {})".format(status))

    def test_iotprovision_error_propagation(self):
        """
        Testing error propagation and reporting
        """
        kit_info = copy(DEFAULT_KIT_INFO)
        exception_msg = "Exception injected in test"

        self._mock_kitprogrammer_obj(kit_info)
        mock_provisioneraws_inst = self.mock_provisioneraws()
        mock_provisioneraws_inst.do_provision.side_effect = KitCommunicationError(exception_msg)


        # Modify certificate folder to avoid permission denied problems when running on Jenkins as the original
        # certificate folder location will be outside the workspace of the build job
        certs_folder = os.path.join(TEST_CERT_ROOT_FOLDER, ".microchip-iot", kit_info["serialnumber"])
        Config.Certs.certs_dir = certs_folder

        # Make sure the certificate folder gets deleted even if the test fails
        self.addCleanup(self._remove_folder, TEST_CERT_ROOT_FOLDER)

        mock_stdout = self._mock_stdout()

        # Run the code to be tested
        testargs = ["iotprovision", "-caws"]
        with patch.object(sys, "argv", testargs):
            status = main()

        # Check that the code executed as expected
        self.assertEqual(status, 1, msg="Command succeeded even though FW communication failed")
        # Check that the correct exception was triggered, captured and logged
        self.assertTrue(exception_msg in mock_stdout.getvalue(), msg="Did not find '{}' in stdout: '{}'".format(exception_msg, mock_stdout.getvalue()))
