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
import unittest
from freezegun import freeze_time

from uc3m_money.transfer_request import TransferRequest
from uc3m_money.account_management_exception import AccountManagementException


class BaseTransferRequestTest(unittest.TestCase):
    """
    Base class providing setUp and tearDown for all TransferRequest tests.
    """

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

class TestTransferRequestValid(BaseTransferRequestTest):
    """
    Tests a fully valid transfer request scenario.
    """
    @freeze_time("2025-03-25 12:00:00")
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
        self.assertEqual(result["time_stamp"], 1742904000.0)
        self.assertEqual(len(tr.transfer_code), 32)
        self.assertTrue(str(tr).startswith("Transfer:"))

class TestTransferRequestIbanValidation(BaseTransferRequestTest):
    """
    Tests for IBAN validation (type, prefix, length).
    """
    # IBAN Validation Tests
    def test_invalid_from_iban_not_string(self):
        """Test that a non-string from_iban raises an exception."""
        invalid = 1234567890123456789012  # Not a string
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(invalid, self.valid_to_iban, self.valid_details)
        self.assertIn("from_iban must be a string", str(cm.exception))

    def test_invalid_to_iban_not_string(self):
        """Test that a non-string to_iban raises an exception."""
        invalid = 9876543210987654321098  # Not a string
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, invalid, self.valid_details)
        self.assertIn("to_iban must be a string", str(cm.exception))

    def test_invalid_from_iban_prefix(self):
        """Test that a from_iban not starting with 'ES' raises an exception."""
        invalid = "FR1234567890123456789012"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(invalid, self.valid_to_iban, self.valid_details)
        self.assertIn("from_iban must start with 'ES'", str(cm.exception))

    def test_invalid_from_iban_wrong_length(self):
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

class TestTransferRequestTypeValidation(BaseTransferRequestTest):
    """
    Tests for transfer_type validation (must be string, must be ORDINARY/URGENT/IMMEDIATE).
    """
    # Transfer Type Validation
    def test_invalid_transfer_type(self):
        """Test that an invalid transfer_type raises an exception."""
        details = self.valid_details.copy()
        details["transfer_type"] = "EXPRESS"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_type must be ORDINARY, URGENT, or IMMEDIATE", str(cm.exception))

    def test_invalid_transfer_type_not_string(self):
        """Test that a non-string transfer_type raises an exception."""
        details = self.valid_details.copy()
        details["transfer_type"] = 123
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_type must be a string", str(cm.exception))

class TestTransferRequestConceptValidation(BaseTransferRequestTest):
    """
    Tests for transfer_concept validation (must be string, two words, alpha, 10-30 chars).
    """
    # Transfer Concept Validation
    def test_invalid_transfer_concept_not_string(self):
        """Test that a non-string transfer_concept raises an exception."""
        details = self.valid_details.copy()
        details["transfer_concept"] = 12345
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_concept must be a string", str(cm.exception))

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

    def test_valid_transfer_concept_min_length(self):
        """Test that a transfer_concept with exactly 10 characters passes validation."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "Pay Checks"  # 10 characters including space
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIsInstance(tr, TransferRequest)

    def test_valid_transfer_concept_max_length(self):
        """Test that a transfer_concept with exactly 30 characters passes validation."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "PaymentAuthorization Request"  # 30 characters
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIsInstance(tr, TransferRequest)

    def test_invalid_transfer_concept_length(self):
        """Test that a transfer_concept with length outside 10-30 characters raises an exception."""
        details = self.valid_details.copy()
        details["transfer_concept"] = "Hey There"  # Only 9 characters total, too short
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_concept must be 10 to 30 characters long", str(cm.exception))

class TestTransferRequestDateValidation(BaseTransferRequestTest):
    """
    Tests for transfer_date validation
    (must be string, valid format, year=2025-2050, day/month range).
    """
    # Transfer Date Validation
    def test_invalid_transfer_date_format(self):
        """Test that an improperly formatted transfer_date raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "2025-01-07"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_date must be in DD/MM/YYYY format", str(cm.exception))

    def test_invalid_transfer_date_not_string(self):
        """Test that a non-string transfer_date raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = 20250325
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_date must be a string", str(cm.exception))

    def test_invalid_transfer_date_year(self):
        """Test that a transfer_date with a year outside allowed range raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "07/01/2051"  # Year 2051 not allowed
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Year must be between 2025 and 2050", str(cm.exception))

    def test_invalid_transfer_date_day_zero(self):
        """Test that a transfer_date with a day of 00 raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "00/01/2025"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Day must be between 1 and 31", str(cm.exception))

    def test_invalid_transfer_date_month_thirteen(self):
        """Test that a transfer_date with a month of 13 raises an exception"""
        details = self.valid_details.copy()
        details["transfer_date"] = "07/13/2025"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Month must be between 1 and 12", str(cm.exception))

    def test_invalid_transfer_date_day_high(self):
        """Test that a transfer_date with a day of 32 raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "32/01/2025"  # valid month, invalid day
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Day must be between 1 and 31", str(cm.exception))

    def test_invalid_transfer_date_month_low(self):
        """Test that a transfer_date with a month of 00 raises an exception."""
        details = self.valid_details.copy()
        details["transfer_date"] = "07/00/2025"  # valid day, invalid month
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("Month must be between 1 and 12", str(cm.exception))

class TestTransferRequestAmountValidation(BaseTransferRequestTest):
    """
    Tests for transfer_amount validation (must be float, 10.00 <= amount <= 10000.00, <=2 decimals).
    """
    # Transfer Amount Validation
    def test_invalid_transfer_amount_not_float(self):
        """Test that a non-float transfer_amount raises an exception."""
        details = self.valid_details.copy()
        details["transfer_amount"] = "100.00"
        with self.assertRaises(AccountManagementException) as cm:
            TransferRequest(self.valid_from_iban, self.valid_to_iban, details)
        self.assertIn("transfer_amount must be a float", str(cm.exception))

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
        details["transfer_amount"] = 10000.01
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

class TestTransferRequestFileAndProperties(BaseTransferRequestTest):
    """
    Tests for duplicate saving, plus property getters and setters.
    """
    @freeze_time("2025-03-25 12:00:00")
    def test_duplicate_transfer(self):
        """Test that saving a duplicate transfer raises an exception."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        tr.save_to_file(self.test_file)
        with self.assertRaises(AccountManagementException) as cm:
            tr.save_to_file(self.test_file)
        self.assertIn("Duplicate transfer detected", str(cm.exception))

    def test_from_iban_getter_and_setter(self):
        """Test getter and setter for from_iban."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.from_iban, self.valid_from_iban)
        new_iban = "ES1111222233334444555566"
        tr.from_iban = new_iban
        self.assertEqual(tr.from_iban, new_iban)

    def test_to_iban_getter_and_setter(self):
        """Test getter and setter for to_iban."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.to_iban, self.valid_to_iban)
        new_iban = "ES9999888877776666555544"
        tr.to_iban = new_iban
        self.assertEqual(tr.to_iban, new_iban)

    def test_transfer_type_getter_and_setter(self):
        """Test getter and setter for transfer_type."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.transfer_type, "ORDINARY")
        tr.transfer_type = "URGENT"
        self.assertEqual(tr.transfer_type, "URGENT")

    def test_transfer_amount_getter_and_setter(self):
        """Test getter and setter for transfer_amount."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.transfer_amount, 40.00)
        tr.transfer_amount = 1000.00
        self.assertEqual(tr.transfer_amount, 1000.00)

    def test_transfer_concept_getter_and_setter(self):
        """Test getter and setter for transfer_concept."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.transfer_concept, "Payment services")
        tr.transfer_concept = "Service Charge"
        self.assertEqual(tr.transfer_concept, "Service Charge")

    def test_transfer_date_getter_and_setter(self):
        """Test getter and setter for transfer_date."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertEqual(tr.transfer_date, "07/01/2025")
        tr.transfer_date = "08/01/2025"
        self.assertEqual(tr.transfer_date, "08/01/2025")

    def test_time_stamp_property(self):
        """Test that time_stamp returns a float timestamp."""
        tr = TransferRequest(self.valid_from_iban, self.valid_to_iban, self.valid_details)
        self.assertIsInstance(tr.time_stamp, float)

if __name__ == "__main__":
    unittest.main()
