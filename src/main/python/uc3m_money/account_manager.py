"""Module for account management operations."""

import json
import datetime
from .account_management_exception import AccountManagementException
from .transfer_request import TransferRequest


class AccountManager:
    """Class for providing the methods for managing accounts."""

    @staticmethod
    def validate_iban(iban: str) -> bool:
        """
        Returns True if the IBAN received is a valid Spanish IBAN, otherwise False.

        A valid Spanish IBAN should:
        - Be a string.
        - Start with 'ES'.
        - Have a total length of 24 characters.
        """
        if not isinstance(iban, str):
            return False
        if not iban.startswith("ES"):
            return False
        if len(iban) != 24:
            return False
        return True

    @staticmethod
    def calculate_balance(iban_number: str) -> bool:
        """
        Calculates the balance for the given IBAN by summing up the amounts from the
        transactions.json file and writes the balance data to a JSON file.

        :param iban_number: A valid IBAN string.
        :return: True if the balance is successfully calculated and stored.
        :raises: AccountManagementException if any error occurs.
        """
        if not AccountManager.validate_iban(iban_number):
            raise AccountManagementException("Invalid IBAN")

        transactions_file = "transactions.json"

        try:
            with open(transactions_file, "r", encoding="utf-8") as file:
                transactions = json.load(file)
        except FileNotFoundError as exc:
            raise AccountManagementException(
                "Transactions file not found"
            ) from exc
        except json.JSONDecodeError as exc:
            raise AccountManagementException(
                "Transactions file is not valid JSON"
            ) from exc

        found = False
        total = 0.0

        for tx in transactions:
            if "IBAN" in tx and tx["IBAN"] == iban_number:
                found = True
                amount_str = tx.get("amount", "")
                # Clean the amount string: remove spaces and replace comma with dot.
                amount_str = amount_str.replace(" ", "").replace(",", ".")
                try:
                    total += float(amount_str)
                except ValueError as exc:
                    raise AccountManagementException(
                        "Invalid amount format in transactions"
                    ) from exc

        if not found:
            raise AccountManagementException("IBAN not found in transactions")

        balance_data = {
            "IBAN": iban_number,
            "timestamp": datetime.datetime.utcnow().timestamp(),
            "balance": total
        }
        balance_file = f"balance_{iban_number}.json"

        try:
            with open(balance_file, "w", encoding="utf-8") as file:
                json.dump(balance_data, file, indent=4)
        except Exception as exc:
            raise AccountManagementException(
                "Error writing balance file: " + str(exc)
            ) from exc

        return True
