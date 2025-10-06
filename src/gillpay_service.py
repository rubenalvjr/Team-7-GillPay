# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: GillPayService

# PURPOSE: Core business logic for GillPay (validation, summaries, reports).

# INPUT: Requests from CLI/GUI to fetch, summarize, and persist transactions.

# PROCESS: Validate and persist transactions via DAO; compute
# income/expense/net summaries; build CLI reports.

# OUTPUT: Dict summaries, PrettyTable console output, and DAO persistence.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Business logic facade for GillPay."""

from __future__ import annotations

import datetime
from typing import Dict, List

from prettytable import PrettyTable

from src.models.transaction import Transaction
from src.dao.transaction_dao import TransactionDAO
from src.dao.category_dao import CategoryDAO


class GillPayService:
    """Service layer encapsulating validation, summaries, and CLI reports."""

    DATE_FMT = "%Y/%m/%d"

    def __init__(self) -> None:
        """Initialize the service and its DAO dependency."""
        self.CategoryDAO = CategoryDAO()
        self.TransactionDAO = TransactionDAO()

    # Data access

    def GetExpenseData(self) -> List[Transaction]:
        """Return all expense transactions."""
        return self.TransactionDAO.GetTransactionsBy("transaction",
                                                     "expense")

    def GetIncomeData(self) -> List[Transaction]:
        """Return all income transactions."""
        return self.TransactionDAO.GetTransactionsBy("transaction",
                                                     "income")

    def GetAllTransactions(self) -> List[Transaction]:
        """Return all transactions."""
        return self.TransactionDAO.GetTransactions()

    # Create / validation

    def PostTransaction(self, NewTransaction: Transaction) -> None:
        """Validate and persist a new transaction; print error message on
        failure."""
        try:
            self.ValidateEntry(NewTransaction)
            self.TransactionDAO.SaveTransaction(NewTransaction)
        except ValueError as ex:
            print(str(ex))

    def ValidateEntry(self, Tx: Transaction) -> None:
        """Validate a transaction; raise ValueError if any rule fails."""
        tx_type = (Tx.transaction or "").strip().lower()
        if tx_type not in {"income", "expense"}:
            raise ValueError(
                "Invalid transaction type. Use 'income' or 'expense'.")

        if not self.DateValidator(Tx.date):
            raise ValueError(
                "You entered an invalid date.\nPlease enter the date in the "
                "format YYYY/MM/DD.")

        allowed_list = self.CategoryDAO.ListCategoryNames(
            "Income" if tx_type == "income" else "Expense")
        needle = (Tx.category or "").strip().casefold()
        is_valid = any(c.casefold() == needle for c in allowed_list)
        if not is_valid:
            allowed = ", ".join(allowed_list)
            raise ValueError(
                f"Invalid category '{Tx.category}' for transaction '"
                f"{tx_type}'.\nAllowed: {allowed}.")

        try:
            amount = float(Tx.amount)
        except Exception:
            raise ValueError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if not (Tx.description or "").strip():
            raise ValueError("Description cannot be empty.")

    def DateValidator(self, DateText: str) -> bool:
        """Return True if the string matches YYYY/MM/DD."""
        try:
            datetime.datetime.strptime(DateText, self.DATE_FMT)
            return True
        except ValueError:
            return False

    # Summaries

    def CalculateSum(self, Items: List[Transaction]) -> float:
        """Return the sum of the amount field across transactions."""
        total = 0.0
        for tx in Items:
            total += float(tx.amount)
        return total

    def GetTransactionSummary(self) -> Dict[str, float]:
        """Return a summary dict with keys: income, expense, net."""
        income = self.CalculateSum(self.GetIncomeData())
        expense = self.CalculateSum(self.GetExpenseData())
        net = income - expense
        return {"income": income, "expense": expense, "net": net}

    # Reports (CLI PrettyTable)

    def GenerateReport(self, ReportType: str) -> None:
        """Print a CLI report. Supported: 'EXP_BY_CAT', 'SUMMARY_BY_MONTH'."""
        table = PrettyTable()

        if ReportType == "EXP_BY_CAT":
            report = self.TransactionDAO.ExpenseByCategoryData()
            table.field_names = ["Category", "Amount"]
            table.title = "Expense By Category"
            for _, row in report.iterrows():
                table.add_row([row["category"], f"${row['amount']:.2f}"])
            print(table)

        elif ReportType == "SUMMARY_BY_MONTH":
            report = self.TransactionDAO.SummaryByMonthData()
            table.field_names = ["Month", "Income", "Expense", "Net"]
            table.title = "Summary By Month"
            for _, row in report.iterrows():
                table.add_row(
                    [
                        str(row["month"]),
                        f"${row['income']:.2f}",
                        f"${row['expense']:.2f}",
                        f"${row['net']:.2f}",
                    ]
                )
            print(table)

        else:
            print(f"Unknown report type: {ReportType}")

    # GUI chart support

    def GetExpenseTotalsByCategory(self) -> Dict[str, float]:
        """Return {DisplayCategory: total} for expenses, collapsing
        case/space variants."""
        df = self.TransactionDAO.ExpenseByCategoryData().copy(deep=True)
        df.loc[:, "category"] = df["category"].astype(str)
        df.loc[:, "__norm"] = df["category"].str.strip().str.lower()
        summed = df.groupby("__norm", as_index=True, sort=False, dropna=False)[
            "amount"].sum()
        name_map = (
            df.loc[:, ["__norm", "category"]]
            .drop_duplicates("__norm", keep="first")
            .set_index("__norm")["category"]
            .apply(lambda s: str(s).strip().title())
            .to_dict()
        )
        return {name_map.get(k, (k or "").title()): float(v) for k, v in
                summed.items()}

    def GetIncomeTotalsByCategory(self) -> Dict[str, float]:
        """Return {DisplayCategory: total} for income, collapsing case/space
        variants."""
        df = self.TransactionDAO.GetDataFrame().copy(deep=True)
        df.loc[:, "transaction"] = df["transaction"].astype(str).str.lower()
        df = df[df["transaction"] == "income"].copy()
        df.loc[:, "category"] = df["category"].astype(str)
        df.loc[:, "__norm"] = df["category"].str.strip().str.lower()
        summed = df.groupby("__norm", as_index=True, sort=False, dropna=False)[
            "amount"].sum()
        name_map = (
            df.loc[:, ["__norm", "category"]]
            .drop_duplicates("__norm", keep="first")
            .set_index("__norm")["category"]
            .apply(lambda s: str(s).strip().title())
            .to_dict()
        )
        return {name_map.get(k, (k or "").title()): float(v) for k, v in
                summed.items()}
