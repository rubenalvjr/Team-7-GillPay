# PROGRAM:     TransactionDAO (DAO - Data Access Object)
# AUTHOR:      Team 7
# PURPOSE:     Data access layer of GillPay application that handles the read
#                   and write operations to application CSV
# INPUT:       Transaction data passed in by clients
# PROCESS:     - When reading CSV us Pandas due to built-in query ability
#              - When writing to CSV use CSV due to simplicity
# OUTPUT:      Returns a List of Transaction when getting data
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

import csv
import pandas
from typing import List
from pandas.core.interchange.dataframe_protocol import DataFrame
from src.transaction import Transaction


class TransactionDAO:

    def __init__(self, datasource="../data/gillpay_data.csv"):
        """
        Constructor with default file path configured
        """
        self.datasource = datasource

    def GetDataFrame(self) -> DataFrame:
        """
        Reads CSV file with Pandas and returns a DataFrame
        """
        return pandas.read_csv(self.datasource)

    def GetTransactions(self) -> list[Transaction] | None:
        """
        Reads all transactions from CSV and returns list of data
        """
        try:
            dataFrame = self.GetDataFrame()
            csvList = dataFrame.values.tolist()
            # Converts list of list to List of Transactions
            return self.ConvertToTransactionList(csvList)
        except FileNotFoundError:
            print(f"Unable to find file {self.datasource}")

    def GetTransactionsBy(self, columName, columnValue) -> List[Transaction]:
        """
        Queries CSV based on column name/value and returns list of data
        """
        dataFrame = self.GetDataFrame()
        # Uses inputs parameters to pull query CSV data
        csvList = dataFrame[dataFrame[columName] == columnValue].values.tolist()
        return self.ConvertToTransactionList(csvList)

    def SaveTransaction(self, transaction: Transaction):
        """
        Takes in passed in Transaction object and appends into CSV
        """
        try:
            # Opens the file in append mode
            with open(self.datasource, "a", newline="") as csv_file:
                csvWriter = csv.writer(csv_file)
                # Pulls Transaction data into a list (row)
                newRow = [transaction.transaction_type,
                          transaction.category,
                          transaction.description,
                          transaction.amount,
                          transaction.date]
                # Appends new row to CSV
                csvWriter.writerow(newRow)
        except FileNotFoundError:
            print(f"Unable to find file {self.datasource}")

    def ConvertToTransactionList(self, csvData) -> List[Transaction]:
        """
        Converts a list of list data to a list of Transactions
        """
        transactionList = []
        for row in csvData:
            transaction = Transaction(
                transaction=row[0],
                category=row[1],
                description=row[2],
                amount=row[3],
                date=row[4])
            transactionList.append(transaction)
        return transactionList
