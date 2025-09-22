# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.
import datetime
from typing import List, Any
from prettytable import PrettyTable
from src.models.transaction import Transaction
from src.dao.transaction_dao import TransactionDAO


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
                       .GetTransactionsBy("transaction", "expense"))

        return expenseData

    def GetIncomeData(self) -> List[Transaction]:
        """
        Calls TransactionDAO to get all instances of Income data
        """
        incomeData = (self.
                      transactionDAO
                      .GetTransactionsBy("transaction", "income"))
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
        if self.DateValidator(transaction.date):
            self.transactionDAO.SaveTransaction(transaction)
        else:
            # Inform user that invalid date/format was entered
            print("You entered an invalid Date!")
            print("Remember enter date in the give formate YYYY/MM/DD")

    def CalculateSum(self, transactionList: List[Transaction]) -> float:
        """
        Calculates sum for a given list of Transactions
        """
        total = 0
        for transaction in transactionList:
            total += transaction.amount
        return total

    def DateValidator(self, date: str) -> bool:
        """
        Checks if date is valid as in proper format
        """
        try:
            # Parses time based on date regex format
            datetime.datetime.strptime(date, "%Y/%m/%d")
            return True
        except ValueError:
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

    def GenerateReport(self, reportType: str):
        """
        Creates a report visualization by on passed in report type. The report
        is displayed in the CLI
        """
        table = PrettyTable()
        if reportType == "EXP_BY_CAT":
            # Retrieve Expense by Report Data needed for building report
            reportData = self.transactionDAO.ExpenseByCategoryData()

            # Set column headers for report
            table.field_names = ["Category", "Amount"]

            # Set report title
            table.title = "Expense By Category"

            # Load data for each row
            for _, row in reportData.iterrows():
                table.add_row([row["category"], f"${row['amount']:.2f}"])
            print(table)

        elif reportType == "SUMMARY_BY_MONTH":
            # Retrieve Summary by Month Data needed for building report
            reportData = self.transactionDAO.SummaryByMonthData()

            # Set column headers for report
            table.field_names = ["Month", "Income", "Expense", "Net"]

            # Set report title
            table.title = "Summary By Month "

            # Load data for each row
            for _, row in reportData.iterrows():
                table.add_row([
                    str(row["month"]),
                    f"${row['income']:.2f}",
                    f"${row['expense']:.2f}",
                    f"${row['net']:.2f}", ])
            print(table)
