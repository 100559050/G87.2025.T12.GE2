"""Contains the class OrderShipping"""
from datetime import datetime, timezone
import hashlib
import json
import os
from uc3m_money.account_management_exception import AccountManagementException

class AccountDeposit:
    """Class representing the information required for shipping of an order"""

    def __init__(self,
                 to_iban: str,
                 deposit_amount):
        self.__alg = "SHA-256"
        self.__type = "DEPOSIT"
        self.__to_iban = to_iban
        self.__deposit_amount = deposit_amount
        justnow = datetime.now(timezone.utc)
        self.__deposit_date = datetime.timestamp(justnow)

        self.validate()

    def to_json(self):
        """returns the object data in json format"""
        return {"alg": self.__alg,
                "typ": self.__type,
                "to_iban": self.__to_iban,
                "deposit_amount": self.__deposit_amount,
                "deposit_date": self.__deposit_date,
                "deposit_signature": self.deposit_signature}

    def validate(self):
        """Validates to_iban and deposit_amount fields."""
        # IBAN validation
        if not isinstance(self.__to_iban, str):
            raise AccountManagementException("to_iban must be a string.")
        if len(self.__to_iban) != 24:
            raise AccountManagementException("to_iban must be exactly 24 characters.")
        if not self.__to_iban.startswith("ES"):
            raise AccountManagementException("to_iban must start with 'ES'.")

        # Deposit amount validation
        if not isinstance(self.__deposit_amount, float):
            raise AccountManagementException("deposit_amount must be a float.")
        if not 10.00 <= self.__deposit_amount <= 10000.00:
            raise AccountManagementException("deposit_amount must be between 10.00 and 10000.00.")
        if "." in str(self.__deposit_amount):
            decimal_part = str(self.__deposit_amount).split(".")[1]
            if len(decimal_part) > 2:
                raise AccountManagementException("deposit_amount must have at most 2 decimal places.")

    def save_to_file(self, file_path="deposits.json"):
        """
        Saves the deposit request to a JSON file.

        If the file exists, it appends the new deposit unless it's a duplicate.
        If the file doesn't exist, it creates a new one.

        Raises:
            AccountManagementException: if there's an error saving or duplicate entry.
        """
        try:
            data = []

            # Load existing data if the file exists
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            # Prevent duplicate deposit entries (exact match)
            if any(entry == self.to_json() for entry in data):
                raise AccountManagementException("Duplicate deposit entry detected.")

            # Append and write back
            data.append(self.to_json())

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except Exception as e:
            raise AccountManagementException(f"Error saving deposit to file: {str(e)}") from e


    def __signature_string(self):
        """Composes the string to be used for generating the key for the date"""
        return "{alg:" + str(self.__alg) +",typ:" + str(self.__type) +",iban:" + \
               str(self.__to_iban) + ",amount:" + str(self.__deposit_amount) + \
               ",deposit_date:" + str(self.__deposit_date) + "}"

    @property
    def to_iban(self):
        """Property that represents the product_id of the patient"""
        return self.__to_iban

    @to_iban.setter
    def to_iban(self, value):
        self.__to_iban = value

    @property
    def deposit_amount(self):
        """Property that represents the order_id"""
        return self.__deposit_amount
    @deposit_amount.setter
    def deposit_amount(self, value):
        self.__deposit_amount = value

    @property
    def deposit_date(self):
        """Property that represents the phone number of the client"""
        return self.__deposit_date
    @deposit_date.setter
    def deposit_date( self, value ):
        self.__deposit_date = value

    @property
    def deposit_signature( self ):
        """Returns the sha256 signature of the date"""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()
