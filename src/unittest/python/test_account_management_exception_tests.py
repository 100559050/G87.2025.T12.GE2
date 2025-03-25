#!/usr/bin/env python
"""Tests for the AccountManager functionality.

This module tests the AccountManagementException class located in:
src/main/python/uc3m_money/account_management_exception.py

"""

import unittest
from uc3m_money.account_management_exception import AccountManagementException

class TestAccountManagementException(unittest.TestCase):
    """Tests for Account Management Exception."""
    def test_message_getter_and_setter(self):
        """Test the getter and setter for AccountManagementException.message."""
        exc = AccountManagementException("Initial error")
        self.assertEqual(exc.message, "Initial error")

        exc.message = "Updated error"
        self.assertEqual(exc.message, "Updated error")

if __name__ == "__main__":
    unittest.main()
