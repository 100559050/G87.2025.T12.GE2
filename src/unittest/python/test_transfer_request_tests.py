#!/usr/bin/env python
"""Tests for the TransferRequest functionality.

This module tests the TransferRequest class located in:
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

from uc3m_money.transfer_request import TransferRequest
from uc3m_money.account_management_exception import AccountManagementException


class TestTransferRequest(unittest.TestCase):
    """Test cases for the TransferRequest class."""

    def setUp(self):
        """Set up valid test fixtures."""
        self.valid_from_iban = "ES1234567890123456789012"  # valid: 24 chars, starts with ES
        self.valid_to_iban = "ES9876543210987654321098"    # valid: 24 chars, starts with ES
        self.valid_details = {
            "transfer_type": "ORDINARY",
            "transfer_concept": "Payment services",  # Two words, only letters, length=16
            "transfer_date": "07/01/2025",            # Year between 2025 and 2050
            "transfer_amount": 40.00,                 # Valid float in range
        }
        # File used for testing save_to_file functionality.
        self.test_file = "test_transfers.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        """Clean up test artifacts."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_valid_transfer_request(self):
        """Test that a valid transfer request is created successfully."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        result = tr.to_json()
        expected_keys = {
            "from_iban",
            "to_iban",
            "transfer_type",
            "transfer_amount",
            "transfer_concept",
            "transfer_date",
            "time_stamp",
            "transfer_code",
        }
        self.assertEqual(set(result.keys()), expected_keys)
        self.assertEqual(len(tr.transfer_code), 32)
        self.assertTrue(str(tr).startswith("Transfer:"))

    # IBAN Validation Tests
    def test_invalid_from_iban_prefix(self):
        """Test that a from_iban not starting with 'ES' raises an exception."""
        invalid = "FR1234567890123456789012"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(invalid, self.valid_to_iban, self.valid_details)
        self.assertIn("from_iban must start with 'ES'", str(cm.exception))

    def test_invalid_from_iban_length_short(self):
        """Test that a from_iban with fewer than 24 characters raises an exception."""
        invalid = "ES123456789012345678901"  # 23 chars
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(invalid, self.valid_to_iban, self.valid_details)
        self.assertIn("must be exactly 24 characters", str(cm.exception))

    def test_invalid_from_iban_length_long(self):
        """Test that a from_iban with more than 24 characters raises an exception."""
        invalid = "ES12345678901234567890123"  # 25 chars
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(invalid, self.valid_to_iban, self.valid_details)
        self.assertIn("must be exactly 24 characters", str(cm.exception))

    def test_invalid_to_iban_prefix(self):
        """Test that a to_iban not starting with 'ES' raises an exception."""
        invalid = "FR9876543210987654321098"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, invalid, self.valid_details)
        self.assertIn("to_iban must start with 'ES'", str(cm.exception))

    # Transfer Type Validation
    def test_invalid_transfer_type(self):
        """Test that an invalid transfer_type raises an exception."""
        details = self.valid_details.copy()
        details["transfer_type"] = "EXPRESS"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_type must be ORDINARY, URGENT, or IMMEDIATE", str(cm.exception))

    # Transfer Concept Validation
    def test_invalid_transfer_concept_one_word(self):
        """Test that a transfer_concept with only one word raises an exception."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "Payment"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_concept must contain exactly two words", str(cm.exception))

    def test_invalid_transfer_concept_nonalpha(self):
        """Test that a transfer_concept containing non-letter characters raises an exception."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "Payment 123"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_concept must contain only letters", str(cm.exception))

    def test_invalid_transfer_concept_length(self):
        """Test that a transfer_concept with length outside 10-30 characters raises an exception."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "Hi There"  # Only 8 characters total, too short
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_concept must be 10 to 30 characters long", str(cm.exception))

    # Transfer Date Validation
    def test_invalid_transfer_date_format(self):
        """Test that an improperly formatted transfer_date raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "2025-01-07"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_date must be in DD/MM/YYYY format", str(cm.exception))

    def test_invalid_transfer_date_year(self):
        """Test that a transfer_date with a year outside allowed range raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "07/01/2051"  # Year 2051 not allowed
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Year must be between 2025 and 2050", str(cm.exception))

    # Transfer Amount Validation
    def test_invalid_transfer_amount_low(self):
        """Test that a transfer_amount lower than 10.00 raises an exception."""
        details = self.valid_details.copy()
        details["transfer_amount"] = 9.99
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_amount must be between 10.00 and 10000.00", str(cm.exception))

    def test_invalid_transfer_amount_high(self):
        """Test that a transfer_amount higher than 10000.00 raises an exception."""
        details = self.valid_details.copy()
        details["transfer_amount"] = 10001.00
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_amount must be between 10.00 and 10000.00", str(cm.exception))

    def test_invalid_transfer_amount_decimals(self):
        """Test that a transfer_amount with more than 2 decimal places raises an exception."""
        details = self.valid_details.copy()
        details["transfer_amount"] = 40.123
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_amount must have at most 2 decimal places", str(cm.exception))

    # File Saving Tests
    def test_save_to_file_success(self):
        """Test that save_to_file correctly writes transfer data to a file."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        # Ensure file does not exist
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        tr.save_to_file(self.test_file)
        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0], tr.to_json())

    def test_duplicate_transfer(self):
        """Test that saving a duplicate transfer raises an exception."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        tr.save_to_file(self.test_file)
        with self.assertRaises(AccountManagementException) as cm:
            tr.save_to_file(self.test_file)
        self.assertIn("Duplicate transfer detected", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
