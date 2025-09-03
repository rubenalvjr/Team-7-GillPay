import csv
import pandas
from collections.abc import Iterable
from pandas.core.interchange.dataframe_protocol import DataFrame
from src.transaction import Transaction


class TransactionDAO:

    def __init__(self, datasource= "../data/gillpay_data.csv"):
        self.datasource = datasource

    def get_data_frame(self) -> DataFrame:
        return pandas.read_csv(self.datasource)

    def get_all_transactions(self) -> Iterable[Transaction]:
        try:
            data_frame = self.get_data_frame()
            return data_frame.values.tolist()
        except FileNotFoundError:
            print(f"Unable to find file {self.datasource}")

    def save_transaction(self, transaction: Transaction):

        try:
            with open(self.datasource, "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                new_row = [transaction.transaction_type, transaction.category,
                           transaction.amount, transaction.date]
                writer.writerow(new_row)
        except FileNotFoundError:
            print(f"Unable to find file {self.datasource}")

    # TODO - Calculate income
    # TODO - Calculate expense


