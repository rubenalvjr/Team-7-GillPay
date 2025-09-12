# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.
from datetime import datetime
from typing import List, Any

from src.transaction import Transaction
from src.transaction_dao import TransactionDAO


class GillPayService:

    def __init__(self):
        """
        Constructor that instantiates a TransactionDAO
        """
        self.transactionDAO = TransactionDAO()

    def GetExpenseData(self) -> List[Transaction]:
        """
        Calls TransactionDAO to get all instances of Expense data
        """
        expenseData = (self.
                       transactionDAO
                       .GetTransactionsBy("type", "expense"))

        return expenseData

    def GetIncomeData(self) -> List[Transaction]:
        """
        Calls TransactionDAO to get all instances of Income data
        """
        incomeData = (self.
                      transactionDAO
                      .GetTransactionsBy("type", "income"))
        return incomeData

    def GetAllTransactions(self) -> List[Transaction]:
        """
        Calls TransactionDAO to get all transactions
        """
        return self.transactionDAO.GetTransactions()

    def PostTransaction(self, transaction: Transaction):
        """
        Calls TransactionDAO to append (POST) a transaction to CSV
        """
        # Check if entered date is valid
        if self.DateValidator(transaction.date) and self.TransactionValidator(
                transaction.transaction_type):
            self.transactionDAO.SaveTransaction(transaction)

    def CalculateSum(self, transactionList: List[Transaction]) -> float:
        """
        Calculates sum for a given list of Transactions
        """
        total = 0
        for transaction in transactionList:
            total += transaction.amount
        return total

    def TransactionValidator(self, transactionType):
        """
        Checks if transaction is correct type (Income/Expense)
        """
        if transactionType == "expense" or transactionType == "income":
            return True
        else:
            # Inform user that invalid transaction type
            print("You entered an invalid data!")
            print("Only Expense and Income are allowed transactions")
            return False

    def DateValidator(self, date: str) -> bool:
        """
        Checks if date is valid as in proper format
        """
        try:
            # Parses time based on date regex format
            datetime.strptime(date, "%Y/%m/%d")
            return True
        except ValueError:
            # Inform user that invalid date/format was entered
            print("You entered an invalid Date!")
            print("Remember enter date in the give formate YYYY/MM/DD")
            return False

    def GetTransactionSummary(self) -> dict[Any, Any]:
        """
        Creates a dictionary containing the summary data of Income, Expense,
        and Net Income
        """
        summaryDictionary = {}
        incomeSummary = self.CalculateSum(self.GetIncomeData())
        expenseSummary = self.CalculateSum(self.GetExpenseData())
        # Calculate Net Income based on Income and Expense data
        netIncomeSummary = incomeSummary - expenseSummary
        # Sets the values of the dictionary for each summary category
        summaryDictionary["income"] = incomeSummary
        summaryDictionary["expense"] = expenseSummary
        summaryDictionary["net"] = netIncomeSummary
        return summaryDictionary
