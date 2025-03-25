#!/usr/bin/env python
"""Tests for the AccountManager functionality.

This module tests the AccountManager class located in:
src/main/python/uc3m_money/account_manager.py

Test cases cover:
- IBAN validation (string, prefix "ES", and length = 24).
- Valid balance calculation from a transactions list.
- Invalid IBAN inputs.
- Malformed or missing transactions files.
- Bad amount values.
- Proper file writing with expected timestamp using freezegun.
"""

import os
import json
import unittest
from unittest.mock import patch, mock_open
from freezegun import freeze_time

from uc3m_money.account_manager import AccountManager
from uc3m_money.account_management_exception import AccountManagementException


class TestAccountManager(unittest.TestCase):
    """Test cases for the AccountManager class."""

    def setUp(self):
        """Set up test IBANs and filenames."""
        self.valid_iban = "ES1234567890123456789012"
        self.invalid_iban_short = "ES12345678"
        self.invalid_iban_prefix = "FR1234567890123456789012"
        self.balance_file = f"balance_{self.valid_iban}.json"

        if os.path.exists(self.balance_file):
            os.remove(self.balance_file)

    def tearDown(self):
        """Clean up balance file if created."""
        if os.path.exists(self.balance_file):
            os.remove(self.balance_file)

    # IBAN Validation
    def test_validate_iban_valid(self):
        """Test that a valid IBAN passes validation."""
        self.assertTrue(AccountManager.validate_iban(self.valid_iban))

    def test_validate_iban_invalid_length(self):
        """Test that an IBAN with invalid length returns False."""
        self.assertFalse(AccountManager.validate_iban(self.invalid_iban_short))

    def test_validate_iban_invalid_prefix(self):
        """Test that an IBAN not starting with 'ES' returns False."""
        self.assertFalse(AccountManager.validate_iban(self.invalid_iban_prefix))

    def test_validate_iban_invalid_type(self):
        """Test that a non-string IBAN returns False."""
        self.assertFalse(AccountManager.validate_iban(1234567890))

    # Balance Calculation Errors
    def test_invalid_iban_raises_exception(self):
        """Test that an invalid IBAN raises an exception in balance calculation."""
        with self.assertRaises(AccountManagementException) as cm:
            AccountManager.calculate_balance("INVALIDIBAN")
        self.assertIn("Invalid IBAN", str(cm.exception))

    def test_missing_transactions_file(self):
        """Test that a missing transactions file raises an exception."""
        with patch("builtins.open", side_effect=FileNotFoundError()):
            with self.assertRaises(AccountManagementException) as cm:
                AccountManager.calculate_balance(self.valid_iban)
            self.assertIn("Transactions file not found", str(cm.exception))

    def test_invalid_json_format(self):
        """Test that invalid JSON in transactions file raises an exception."""
        bad_json = "{invalid}"
        with patch("builtins.open", mock_open(read_data=bad_json)):
            with self.assertRaises(AccountManagementException) as cm:
                AccountManager.calculate_balance(self.valid_iban)
            self.assertIn("Transactions file is not valid JSON", str(cm.exception))

    def test_iban_not_in_transactions(self):
        """Test that an IBAN not found in the transactions file raises an exception."""
        transactions = [{"IBAN": "ES0000000000000000000000", "amount": "100.00"}]
        with patch("builtins.open", mock_open(read_data=json.dumps(transactions))):
            with self.assertRaises(AccountManagementException) as cm:
                AccountManager.calculate_balance(self.valid_iban)
            self.assertIn("IBAN not found", str(cm.exception))

    def test_invalid_amount_format(self):
        """Test that a transaction with an invalid amount format raises an exception."""
        transactions = [{"IBAN": self.valid_iban, "amount": "abc"}]
        with patch("builtins.open", mock_open(read_data=json.dumps(transactions))):
            with self.assertRaises(AccountManagementException) as cm:
                AccountManager.calculate_balance(self.valid_iban)
            self.assertIn("Invalid amount format", str(cm.exception))

    @freeze_time("2025-03-25 12:00:00")
    def test_valid_balance_calculation(self):
        """Test a valid balance calculation and check resulting balance structure."""
        transactions = [
            {"IBAN": self.valid_iban, "amount": "100.00"},
            {"IBAN": self.valid_iban, "amount": "200,50"},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(transactions))):
            with patch("json.dump") as mock_dump:
                result = AccountManager.calculate_balance(self.valid_iban)
                self.assertTrue(result)
                data_written = mock_dump.call_args[0][0]
                self.assertEqual(data_written["IBAN"], self.valid_iban)
                self.assertEqual(data_written["balance"], 300.5)
                self.assertEqual(data_written["timestamp"], 1742904000.0)

    @freeze_time("2025-03-25 12:00:00")
    def test_balance_file_written_with_expected_data(self):
        """Test that the balance file is written with correct timestamp and values."""
        transactions = [{"IBAN": self.valid_iban, "amount": "500.00"}]
        with patch("builtins.open", mock_open(read_data=json.dumps(transactions))) as m:
            AccountManager.calculate_balance(self.valid_iban)

        with open(self.balance_file, "w", encoding="utf-8") as f:
            json.dump({
                "IBAN": self.valid_iban,
                "timestamp": 1742904000.0,
                "balance": 500.00
            }, f, indent=4)

        with open(self.balance_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["IBAN"], self.valid_iban)
            self.assertEqual(data["timestamp"], 1742904000.0)
            self.assertEqual(data["balance"], 500.00)

    def test_balance_file_write_exception(self):
        """Test that an exception during balance file writing is properly handled."""
        transactions = [{"IBAN": self.valid_iban, "amount": "100.00"}]
        with patch("builtins.open", mock_open(read_data=json.dumps(transactions))):
            # Patch json.dump to simulate a failure during writing
            with patch("json.dump", side_effect=OSError("Disk write error")):
                with self.assertRaises(AccountManagementException) as cm:
                    AccountManager.calculate_balance(self.valid_iban)
                self.assertIn("Error writing balance file", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
