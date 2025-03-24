#!/usr/bin/env python
"""Tests for the AccountDeposit functionality.

This module tests the AccountDeposit class located in:
src/main/python/uc3m_money/account_deposit.py

Make sure your PYTHONPATH includes the main code directory.
For example, from your project root run:
    export PYTHONPATH=$(pwd)/src/main/python
    python -m unittest discover -s src/unittest/python -p "test_account_deposit_tests.py"
"""

import os
import sys
import json  # Added import for json
import unittest

# Adjust sys.path so that the uc3m_money package is found.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../main/python")))

from uc3m_money.account_deposit import AccountDeposit  # pylint: disable=import-error
from uc3m_money.account_management_exception import AccountManagementException  # pylint: disable=import-error


class TestAccountDeposit(unittest.TestCase):
    """Test cases for the AccountDeposit class."""

    def setUp(self):
        """Set up test fixtures for AccountDeposit tests."""
        self.valid_to_iban = "ES1234567890123456789012"
        self.valid_deposit_amount = 100.00  # valid float between 10.00 and 10000.00
        # Create an AccountDeposit instance with valid data.
        self.ad = AccountDeposit(self.valid_to_iban, self.valid_deposit_amount)
        # Use a dedicated file for testing file saving.
        self.file_path = "deposits_test.json"
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def tearDown(self):
        """Clean up test artifacts after tests."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_to_json_returns_expected_keys(self):
        """Test that to_json returns a dictionary with all expected keys."""
        result = self.ad.to_json()
        expected_keys = {"alg", "typ", "to_iban", "deposit_amount", "deposit_date", "deposit_signature"}
        self.assertEqual(set(result.keys()), expected_keys)

    def test_deposit_signature_length(self):
        """Test that the deposit signature is 64 characters long (SHA256 hash)."""
        signature = self.ad.deposit_signature
        self.assertEqual(len(signature), 64)

    def test_invalid_to_iban(self):
        """Test that an invalid to_iban (wrong prefix or length) raises an exception."""
        with self.assertRaises(AccountManagementException):
            AccountDeposit("FR1234567890123456789012", self.valid_deposit_amount)
        with self.assertRaises(AccountManagementException):
            AccountDeposit("ES123456789012345678901", self.valid_deposit_amount)

    def test_invalid_deposit_amount(self):
        """Test that an invalid deposit_amount (out of range) raises an exception."""
        with self.assertRaises(AccountManagementException):
            AccountDeposit(self.valid_to_iban, 5.00)
        with self.assertRaises(AccountManagementException):
            AccountDeposit(self.valid_to_iban, 10001.00)

    def test_save_to_file_success(self):
        """Test that save_to_file correctly writes deposit data to a file."""
        self.ad.save_to_file(self.file_path)
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertTrue(len(data) >= 1)
        self.assertIn("deposit_signature", data[0])

    def test_duplicate_deposit(self):
        """Test that attempting to save a duplicate deposit raises an exception."""
        self.ad.save_to_file(self.file_path)
        with self.assertRaises(AccountManagementException):
            self.ad.save_to_file(self.file_path)


if __name__ == "__main__":
    unittest.main()
