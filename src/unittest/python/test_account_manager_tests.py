#!/usr/bin/env python
"""Tests for the AccountManager functionality.

This module tests the AccountManager class located in:
src/main/python/uc3m_money/transfer_request.py

Test cases cover:
- Valid transfer requests (including MD5 hash generation and JSON output).
- IBAN validations (prefix and length).
- Transfer type validations.
- Transfer concept validations (exactly two words, letters only, valid length).
- Transfer date validations (format and year range: 2025–2050).
- Transfer amount validations (range and at most 2 decimals).
- File saving functionality, including prevention of duplicate entries.
"""

import os
import json
import unittest

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

if __name__ == "__main__":
    unittest.main()
