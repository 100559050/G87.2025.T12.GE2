"""MODULE: transfer_request. Contains the transfer request class"""

import hashlib
import json
from datetime import datetime, timezone
from uc3m_money.account_management_exception import AccountManagementException


class TransferRequest:
    """Class representing a transfer request"""

    def __init__(self, from_iban: str, to_iban: str, transfer_details: dict):
        """
        Initializes a new TransferRequest.

        :param from_iban: Sender's IBAN.
        :param to_iban: Receiver's IBAN.
        :param transfer_details: Dictionary containing:
            - transfer_type: str
            - transfer_concept: str
            - transfer_date: str
            - transfer_amount: float
        """
        self.__from_iban = from_iban
        self.__to_iban = to_iban
        self.__transfer_type = transfer_details.get("transfer_type")
        self.__transfer_concept = transfer_details.get("transfer_concept")
        self.__transfer_date = transfer_details.get("transfer_date")
        self.__transfer_amount = transfer_details.get("transfer_amount")
        justnow = datetime.now(timezone.utc)
        self.__time_stamp = datetime.timestamp(justnow)

        # Run validation
        self.validate()

    def __str__(self):
        return "Transfer:" + json.dumps(self.__dict__)

    def to_json(self):
        """Returns the object information in JSON format."""
        return {
            "from_iban": self.__from_iban,
            "to_iban": self.__to_iban,
            "transfer_type": self.__transfer_type,
            "transfer_amount": self.__transfer_amount,
            "transfer_concept": self.__transfer_concept,
            "transfer_date": self.__transfer_date,
            "time_stamp": self.__time_stamp,
            "transfer_code": self.transfer_code,
        }

    def validate(self):
        """Validates all fields of the transfer request."""
        self._validate_iban(self.__from_iban, "from_iban")
        self._validate_iban(self.__to_iban, "to_iban")
        self._validate_transfer_type()
        self._validate_transfer_concept()
        self._validate_transfer_date()
        self._validate_transfer_amount()

    def _validate_iban(self, iban, name):
        if not isinstance(iban, str):
            raise AccountManagementException(f"{name} must be a string.")
        if len(iban) != 24:
            raise AccountManagementException(f"{name} must be exactly 24 characters.")
        if not iban.startswith("ES"):
            raise AccountManagementException(f"{name} must start with 'ES'.")

    def _validate_transfer_type(self):
        if not isinstance(self.__transfer_type, str):
            raise AccountManagementException("transfer_type must be a string.")
        if self.__transfer_type not in ["ORDINARY", "URGENT", "IMMEDIATE"]:
            raise AccountManagementException("transfer_type must be ORDINARY, URGENT, or IMMEDIATE")

    def _validate_transfer_concept(self):
        if not isinstance(self.__transfer_concept, str):
            raise AccountManagementException("transfer_concept must be a string.")
        concept = self.__transfer_concept.strip()
        parts = concept.split(" ")
        if len(parts) != 2:
            raise AccountManagementException("transfer_concept must contain exactly two words.")
        if not all(part.isalpha() for part in parts):
            raise AccountManagementException("transfer_concept must contain only letters.")
        if not 10 <= len(concept) <= 30:
            raise AccountManagementException("transfer_concept must be 10 to 30 characters long.")

    def _validate_transfer_date(self):
        if not isinstance(self.__transfer_date, str):
            raise AccountManagementException("transfer_date must be a string.")
        try:
            day, month, year = map(int, self.__transfer_date.split("/"))
        except ValueError as exc:
            raise AccountManagementException("transfer_date must be in DD/MM/YYYY format.") from exc
        if not 1 <= day <= 31:
            raise AccountManagementException("Day must be between 1 and 31.")
        if not 1 <= month <= 12:
            raise AccountManagementException("Month must be between 1 and 12.")
        if not 2025 <= year < 2051:
            raise AccountManagementException("Year must be between 2025 and 2050.")

    def _validate_transfer_amount(self):
        if not isinstance(self.__transfer_amount, float):
            raise AccountManagementException("transfer_amount must be a float.")
        if not 10.00 <= self.__transfer_amount <= 10000.00:
            raise AccountManagementException("transfer_amount must be between 10.00 and 10000.00.")
        if len(f"{self.__transfer_amount:.2f}".split(".")[1]) > 2:
            raise AccountManagementException("transfer_amount must have at most 2 decimal places.")

    @property
    def from_iban(self):
        """Sender's IBAN"""
        return self.__from_iban

    @from_iban.setter
    def from_iban(self, value):
        self.__from_iban = value

    @property
    def to_iban(self):
        """Receiver's IBAN"""
        return self.__to_iban

    @to_iban.setter
    def to_iban(self, value):
        self.__to_iban = value

    @property
    def transfer_type(self):
        """Property representing the type of transfer: REGULAR, IMMEDIATE or URGENT"""
        return self.__transfer_type

    @transfer_type.setter
    def transfer_type(self, value):
        self.__transfer_type = value

    @property
    def transfer_amount(self):
        """Property representing the transfer amount"""
        return self.__transfer_amount

    @transfer_amount.setter
    def transfer_amount(self, value):
        self.__transfer_amount = value

    @property
    def transfer_concept(self):
        """Property representing the transfer concept"""
        return self.__transfer_concept

    @transfer_concept.setter
    def transfer_concept(self, value):
        self.__transfer_concept = value

    @property
    def transfer_date(self):
        """Property representing the transfer's date"""
        return self.__transfer_date

    @transfer_date.setter
    def transfer_date(self, value):
        self.__transfer_date = value

    @property
    def time_stamp(self):
        """Read-only property that returns the timestamp of the request"""
        return self.__time_stamp

    @property
    def transfer_code(self):
        """Returns the MD5 signature (transfer code)"""
        return hashlib.md5(str(self).encode()).hexdigest()
