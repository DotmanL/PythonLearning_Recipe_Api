"""
Test custom Django management commands
"""

from unittest.mock import patch, MagicMock

from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# The patch decorator here is being used to mock the check method in the wait_for_db. file
@patch("core.management.commands.wait_for_db.Command.check")
class CommandTests(SimpleTestCase):
    """Test commands."""

    def test_wait_for_db_ready(self, patched_check: MagicMock) -> None:
        """Test waiting for database if database ready."""
        patched_check.return_value = True

        call_command("wait_for_db")

        patched_check.assert_called_once_with(databases=["default"])

    # Note: patches are passed in the reverse order as arguments, last called patch should be passed first
    @patch("time.sleep")
    def test_wait_for_db_delay(
        self, patched_sleep: MagicMock, patched_check: MagicMock
    ):
        """Test waiting for database when getting OperationalError."""
        # the code below use to mock throwing an exception when testing,
        # (* 2) means the first two times we call the method we want raise the Psycopg2Error
        # (* 3) the next 3 times, we raise the Operational Error
        # the 6th time we get True
        patched_check.side_effect = (
            [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        )

        call_command("wait_for_db")

        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=["default"])
