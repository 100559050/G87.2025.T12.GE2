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
