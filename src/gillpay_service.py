# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.
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
        Call TransactionDAO to get all instances of Expense data
        """
        expenseData = (self.
                       transactionDAO
                       .GetTransactionBy("type", "expense"))

        return expenseData

    def GetIncomeData(self) -> List[Transaction]:
        """
        Call TransactionDAO to get all instances of Income data
        """
        incomeData = (self.
                      transactionDAO
                      .GetTransactionBy("type", "income"))
        return incomeData

    def GetAllTransactions(self) -> List[Transaction]:
        """
        Call TransactionDAO to get all transactions
        """
        return self.transactionDAO.GetTransactions()

    def PostTransaction(self, transaction: Transaction):
        """
        Call TransactionDAO to append (POST) a transaction to CSV
        """
        # TODO - Input validation
        self.transactionDAO.SaveTransaction(transaction)

    def CalculateSum(self, transactionList: List[Transaction]) -> float:
        total = 0
        for transaction in transactionList:
            total += transaction.amount
        return total

    def GetTransactionSummary(self) -> dict[Any, Any]:
        summaryDictionary = {}
        incomeSummary = self.CalculateSum(self.GetIncomeData())
        expenseSummary = self.CalculateSum(self.GetExpenseData())
        netIncomeSummary = incomeSummary - expenseSummary
        summaryDictionary["income"] = incomeSummary
        summaryDictionary["expense"] = expenseSummary
        summaryDictionary["net"] = netIncomeSummary
        return summaryDictionary
