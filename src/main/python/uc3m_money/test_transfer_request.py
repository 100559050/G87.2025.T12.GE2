"""Tests for the TransferRequest module.
This module tests the functionality of the TransferRequest class.
"""

import unittest
from uc3m_money.transfer_request import TransferRequest


class TestTransferRequest(unittest.TestCase):
    """Test cases for the TransferRequest class."""

    def setUp(self):
        """Set up test fixtures for TransferRequest tests."""
        self.from_iban = "ES1234567890123456789012"
        self.to_iban = "ES2109876543210987654321"
        self.transfer_details = {
            "transfer_type": "REGULAR",
            "transfer_concept": "Payment for services",
            "transfer_date": "07/01/2025",
            "transfer_amount": 100.50
        }
        self.tr = TransferRequest(self.from_iban, self.to_iban, self.transfer_details)

    def test_to_json_returns_expected_keys(self):
        """Test that to_json returns a dictionary with all expected keys."""
        result = self.tr.to_json()
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

    def test_transfer_code_length(self):
        """Test that the transfer code is 32 characters long (MD5 hash)."""
        self.assertEqual(len(self.tr.transfer_code), 32)

    def test_str_method_format(self):
        """Test that the __str__ method output starts with 'Transfer:'."""
        self.assertTrue(str(self.tr).startswith("Transfer:"))


if __name__ == "__main__":
    unittest.main()
