# AUTHOR: Matthew Bennett

# DATE: 12SEP2025

# PROGRAM: TransactionDAO

# PURPOSE: Data access layer of GillPay application that handles the read
# and write operations to the application CSV.

# INPUT: Transaction data passed in by clients.

# PROCESS:
# - Read CSV using Pandas for simple querying.
# - Write CSV using csv module for simple appends.

# OUTPUT: Returns a list of Transaction when getting data.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

import csv
from pathlib import Path
from typing import Iterable
import pandas as pd
from pandas import DataFrame
from src.models.transaction import Transaction
from datetime import datetime

_DATE_IN_FORMATS = ("%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y")


def _normalize_date_str(s: str) -> str:
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in _DATE_IN_FORMATS:
        try:
            return datetime.strptime(s, fmt).strftime("%Y/%m/%d")
        except ValueError:
            continue
    return s


class TransactionDAO:
    """
    Minimal DAO with a single, consistent CSV schema:
      ["transaction", "category", "description", "amount", "date"]
    """

    COLUMNS: list[str] = ["transaction", "category", "description", "amount",
                          "date"]

    def __init__(self, datasource: str | None = None):
        """
        Resolve the CSV to <repo>/data/gillpay_data.csv if not provided.
        Ensure the file exists with the correct header.
        """
        if datasource is None:
            repo_root = Path(__file__).resolve().parents[2]
            self.csv_path = repo_root / "data" / "gillpay_data.csv"
        else:
            self.csv_path = Path(datasource).resolve()

        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            self.csv_path.write_text(",".join(self.COLUMNS) + "\n",
                                     encoding="utf-8")

        # String path for Pandas and callers that expect a str
        self.datasource = str(self.csv_path)

    # ---------- Reads ----------

    def GetDataFrame(self) -> DataFrame:

        try:
            df = pd.read_csv(self.datasource, dtype=str)  # everything as string
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.COLUMNS)

        # Ensure expected columns exist
        for col in self.COLUMNS:
            if col not in df.columns:
                df[col] = "0" if col == "amount" else ""

        # reorder & copy (definite copy; no chained-assignment risk)
        df = df[self.COLUMNS].copy()

        # amount = float; others already strings
        df.loc[:, "amount"] = (
            pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(
                float))
        # normalize date display/storage to YYYY/MM/DD
        df.loc[:, "date"] = df["date"].map(_normalize_date_str)

        return df

    def GetTransactions(self) -> list[Transaction]:
        """Return all transactions as Transaction objects."""
        df = self.GetDataFrame()
        return self.ConvertToTransactionList(df.values.tolist())

    def GetTransactionsBy(self, column_name: str, column_value) -> list[
        Transaction]:
        """
        Filter by column name/value and return transactions.

        :param column_name: one of COLUMNS
        :param column_value: value to match in the given column
        """
        if column_name not in self.COLUMNS:
            raise ValueError(
                f"Unknown column '{column_name}'. Expected one of "
                f"{self.COLUMNS}.")

        df = self.GetDataFrame()
        rows = df[df[column_name] == column_value].values.tolist()
        return self.ConvertToTransactionList(rows)

    # ---------- Writes ----------

    def SaveTransaction(self, tx: Transaction) -> None:
        """Append a Transaction to the CSV using the canonical column order."""
        row = [
            str(tx.transaction),
            str(tx.category),
            str(tx.description),
            float(tx.amount),
            _normalize_date_str(str(tx.date)),
        ]
        with self.csv_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)

    def SaveTransactions(self, transactions: Iterable[Transaction]) -> None:
        """Append multiple transactions efficiently."""
        if not transactions:
            return
        with self.csv_path.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            for tx in transactions:
                writer.writerow([
                    str(tx.transaction),
                    str(tx.category),
                    str(tx.description),
                    float(tx.amount),
                    _normalize_date_str(str(tx.date)),
                ])

    # ---------- Helpers ----------

    def ConvertToTransactionList(self, csv_rows) -> list[Transaction]:
        """Convert list-of-lists rows to Transaction objects."""
        items: list[Transaction] = []
        for r in csv_rows:
            items.append(
                Transaction(
                    transaction=str(r[0]),
                    category=str(r[1]),
                    description=str(r[2]),
                    amount=float(r[3]) if r[3] not in ("", None) else 0.0,
                    date=str(r[4]),
                )
            )
        return items

    def ExpenseByCategoryData(self) -> DataFrame:
        """
        Create an Expense by Category DataFrame so that information can be
        passed
        to client to be turned into a visualization
        """
        df = self.GetDataFrame()
        # Pull only expense items
        expenses = df[df["transaction"] == "expense"]

        # Grouping and summing transactions by category and returning DataFrame
        report = expenses.groupby('category')['amount'].sum().reset_index()

        # Sorting items in the amount
        return report.sort_values(by="amount", ascending=False)

    def SummaryByMonthData(self) -> DataFrame:
        """
        Return DataFrame with columns: month ('FullMonth YYYY'), income, expense, net.
        Months are normalized and sorted chronologically here so the UI
        can just consume in order with no extra parsing/sorting.
        """
        df = self.GetDataFrame().copy()

        # Normalize transaction labels to lowercase so unstack yields 'income'/'expense'
        df.loc[:, "transaction"] = df["transaction"].astype(
            str).str.strip().str.lower()

        # Dates are already 'YYYY/MM/DD' from GetDataFrame()
        dt = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
        df = df.loc[dt.notna()].copy()
        df.loc[:, "__month"] = dt.dt.to_period("M")

        # Aggregate income/expense by month
        gb = df.groupby(["__month", "transaction"], observed=True)["amount"].sum()
        pt = gb.unstack(fill_value=0.0)  # columns are exactly ['income','expense'] after the normalization above

        # Ensure columns exist and types are numeric
        for col in ("income", "expense"):
            if col not in pt.columns:
                pt[col] = 0.0
        pt = pt.astype({"income": "float64", "expense": "float64"}, errors="ignore")

        # Net
        pt.loc[:, "net"] = pt["income"] - pt["expense"]

        # Flatten, sort, and build a safe copy before adding new columns
        out = pt.reset_index().sort_values("__month").copy()
        # Friendly month label so tab_report_month can sort with "%B %Y"
        out.loc[:, "month"] = out["__month"].dt.to_timestamp().dt.strftime("%B %Y")

        # Final column order (split into two steps)
        out = out.drop(columns="__month")
        out = out.loc[:, ["month", "income", "expense", "net"]]
        return out
