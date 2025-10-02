# AUTHOR: Team 7

# DATE: 28SEP2025

# PROGRAM: GillPayService

# PURPOSE: Core business logic for GillPay (validation, summaries, reports)

# INPUT: Requests from CLI/GUI to fetch, summarize, and persist transactions

# PROCESS:
# - Validate and persist transactions via the DAO
# - Compute summaries for income, expense, and net
# - Produce CLI table reports (PrettyTable) by category and by month
# - Provide category totals to support the Turtle chart in the CLI

# OUTPUT: Dict summaries, PrettyTable console output, and DAO persistence

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

from __future__ import annotations

import datetime
from typing import Dict, List

from prettytable import PrettyTable

from src.models.transaction import Transaction
from src.dao.transaction_dao import TransactionDAO
from .categories import IsValidCategory, AllowedCategoriesForType




class GillPayService:
    DATE_FMT = "%Y/%m/%d"

    """Business logic facade for GillPay.

    Responsibilities
    ----------------
    - Validate dates for new transactions and forward to the DAO.
    - Provide filtered transaction lists (income vs expense).
    - Compute account summaries (income, expense, net).
    - Render CLI reports using PrettyTable (by category, by month).
    - Expose expense totals by category for the Turtle chart.
    """

    def __init__(self) -> None:
        """Initialize the service and its DAO dependency."""
        self.TransactionDAO = TransactionDAO()

    # ----------------------------
    # Data access helpers
    # ----------------------------
    def GetExpenseData(self) -> List[Transaction]:
        """Return all expense transactions."""
        ExpenseData = self.TransactionDAO.GetTransactionsBy("transaction", "expense")
        return ExpenseData

    def GetIncomeData(self) -> List[Transaction]:
        """Return all income transactions."""
        IncomeData = self.TransactionDAO.GetTransactionsBy("transaction", "income")
        return IncomeData

    def GetAllTransactions(self) -> List[Transaction]:
        """Return all transactions."""
        return self.TransactionDAO.GetTransactions()

    # ----------------------------
    # Create / validation
    # ----------------------------
    def PostTransaction(self, NewTransaction: Transaction) -> None:
        """
        Validate and persist a new transaction.
        Prints a clear message if validation fails.
        """
        try:
            self.ValidateEntry(NewTransaction)
            self.TransactionDAO.SaveTransaction(NewTransaction)
        except ValueError as ex:
            print(str(ex))

    def ValidateEntry(self, Tx: Transaction) -> None:
        """
        Raise ValueError if the transaction fails any business rule checks.
        * Transaction type must be 'income' or 'expense'
        * Date must be YYYY/MM/DD
        * Category must be allowed for the given type
        * Amount must be a number > 0 (store expenses as positive)
        * Description must be non-empty
        """
        TxType = (Tx.transaction or "").strip().lower()
        if TxType not in {"income", "expense"}:
            raise ValueError(
                "Invalid transaction type. Use 'income' or 'expense'.")

        if not self.DateValidator(Tx.date):
            raise ValueError(
                "You entered an invalid date.\nPlease enter the date in the format YYYY/MM/DD."
            )

        # Ensure category is valid for the given transaction type
        if not IsValidCategory(TxType, Tx.category):
            Allowed = ", ".join(AllowedCategoriesForType(
                "Income" if TxType == "income" else "Expense"))
            raise ValueError(
                f"Invalid category '{Tx.category}' for transaction '{TxType}'.\nAllowed: {Allowed}."
            )

        # Amount must be numeric and strictly greater than zero
        try:
            Amount = float(Tx.amount)
        except Exception:
            raise ValueError("Amount must be a number.")
        if Amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        # Description must be present
        if not (Tx.description or "").strip():
            raise ValueError("Description cannot be empty.")

    def DateValidator(self, DateText: str) -> bool:
        """Return True if *DateText* matches YYYY/MM/DD."""
        try:
            datetime.datetime.strptime(DateText, self.DATE_FMT)
            return True
        except ValueError:
            return False

    # ----------------------------
    # Summaries
    # ----------------------------
    def CalculateSum(self, Items: List[Transaction]) -> float:
        """Return the sum of the *amount* field across transactions."""
        Total = 0.0
        for Tx in Items:
            Total += float(Tx.amount)
        return Total

    def GetTransactionSummary(self) -> Dict[str, float]:
        """Return a summary dict with keys: 'income', 'expense', 'net'."""
        IncomeSummary = self.CalculateSum(self.GetIncomeData())
        ExpenseSummary = self.CalculateSum(self.GetExpenseData())
        NetSummary = IncomeSummary - ExpenseSummary
        return {"income": IncomeSummary, "expense": ExpenseSummary, "net": NetSummary}

    # ----------------------------
    # Reports (CLI PrettyTable)
    # ----------------------------
    def GenerateReport(self, ReportType: str) -> None:
        """Print a CLI report for the given report type.

        Supported values
        ----------------
        - "EXP_BY_CAT": Expense by Category totals (descending)
        - "SUMMARY_BY_MONTH": Income/Expense/Net by month
        """
        Table = PrettyTable()

        if ReportType == "EXP_BY_CAT":
            ReportData = self.TransactionDAO.ExpenseByCategoryData()
            Table.field_names = ["Category", "Amount"]
            Table.title = "Expense By Category"
            for _, Row in ReportData.iterrows():
                Table.add_row([Row["category"], f"${Row['amount']:.2f}"])
            print(Table)

        elif ReportType == "SUMMARY_BY_MONTH":
            ReportData = self.TransactionDAO.SummaryByMonthData()
            Table.field_names = ["Month", "Income", "Expense", "Net"]
            Table.title = "Summary By Month"
            for _, Row in ReportData.iterrows():
                Table.add_row([
                    str(Row["month"]),
                    f"${Row['income']:.2f}",
                    f"${Row['expense']:.2f}",
                    f"${Row['net']:.2f}",
                ])
            print(Table)

        else:
            print(f"Unknown report type: {ReportType}")

    # ----------------------------
    # GUI chart support
    # ----------------------------
    def GetExpenseTotalsByCategory(self) -> Dict[str, float]:
        """
        Return {DisplayCategory: total} for expenses, collapsing case/space variants
        (e.g., 'Food', ' food ', 'FOOD' => 'Food'). Uses .loc to avoid chained-assignment warnings.
        """
        # Break any view coming from the DAO
        df = self.TransactionDAO.ExpenseByCategoryData().copy(deep=True)

        # Normalize safely (no chained assignment)
        df.loc[:, "category"] = df["category"].astype(str)
        df.loc[:, "__norm"] = df["category"].str.strip().str.lower()

        # Sum by normalized key
        summed = df.groupby("__norm", as_index=True, sort=False, dropna=False)[
            "amount"].sum()

        # Pick a readable display name (first seen original, trimmed & title-cased)
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
        """
        Return {DisplayCategory: total} for incomes, collapsing case/space variants
        (e.g., 'Salary', ' salary ', 'SALARY' => 'Salary').
        """
        df = self.TransactionDAO.GetDataFrame().copy(deep=True)

        # Normalize safely
        df.loc[:, "transaction"] = df["transaction"].astype(str).str.lower()
        df = df[df["transaction"] == "income"].copy()

        df.loc[:, "category"] = df["category"].astype(str)
        df.loc[:, "__norm"] = df["category"].str.strip().str.lower()

        # Sum by normalized key
        summed = df.groupby("__norm", as_index=True, sort=False, dropna=False)[
            "amount"].sum()

        # Choose readable display names (first seen original, trimmed & title-cased)
        name_map = (
            df.loc[:, ["__norm", "category"]]
            .drop_duplicates("__norm", keep="first")
            .set_index("__norm")["category"]
            .apply(lambda s: str(s).strip().title())
            .to_dict()
        )

        return {name_map.get(k, (k or "").title()): float(v) for k, v in
                summed.items()}
