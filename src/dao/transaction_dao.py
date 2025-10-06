# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: TransactionDAO

# PURPOSE: Data access layer for GillPay that reads and writes transactions
# to CSV.

# INPUT: CSV path (optional) and transaction parameters from callers.

# PROCESS: Load data with Pandas for querying; append rows with csv.writer;
# normalize dates.

# OUTPUT: DataFrames for UI/reporting and lists of Transaction objects.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Transaction CSV DAO used by GillPay."""

import csv
from pathlib import Path
from typing import Iterable
from datetime import datetime

import pandas as pd
from pandas import DataFrame

from src.models.transaction import Transaction

# Accepted input date formats.
DateInFormats = (
    "%Y/%m/%d",  # 2025/10/05
    "%Y-%m-%d",  # 2025-10-05
    "%m/%d/%Y",  # 10/05/2025
    "%m-%d-%Y",  # 10-05-2025
    "%d %b %Y",  # 05 Oct 2025
    "%d %B %Y",  # 05 October 2025
)


def NormalizeDateStr(s: str) -> str:
    """Normalize many common date strings to 'YYYY/MM/DD'.
    Returns '' for falsy input; returns original string when unparseable.
    """
    s = (s or "").strip()
    if not s:
        return ""
    for fmt in DateInFormats:
        try:
            return datetime.strptime(s, fmt).strftime("%Y/%m/%d")
        except ValueError:
            continue
    return s


class TransactionDAO:
    """DAO with a single CSV schema: ['transaction', 'category',
    'description', 'amount', 'date'].

    Public methods provide:
      - Raw and filtered DataFrames
      - List conversions for UI
      - Aggregations: ExpenseByCategoryData, IncomeByCategoryData,
        AllByCategoryData, SummaryByMonthData
    """

    COLUMNS: list[str] = ["transaction", "category", "description", "amount",
                          "date"]

    def __init__(self, datasource: str | None = None):
        """Bind to <repo>/data/gillpay_data.csv unless a custom path is
        provided; ensure header exists."""
        if datasource is None:
            repo_root = Path(__file__).resolve().parents[2]
            self.CsvPath = repo_root / "data" / "gillpay_data.csv"
        else:
            self.CsvPath = Path(datasource).resolve()

        self.CsvPath.parent.mkdir(parents=True, exist_ok=True)
        if not self.CsvPath.exists():
            self.CsvPath.write_text(",".join(self.COLUMNS) + "\n",
                                    encoding="utf-8")

        self.Datasource = str(self.CsvPath)

    # -------------------------
    # Core load/query helpers
    # -------------------------

    def GetDataFrame(self) -> DataFrame:
        """Load all transactions as a DataFrame with normalized types and
        date format."""
        try:
            df = pd.read_csv(self.Datasource, dtype=str)
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.COLUMNS)

        # Ensure all expected columns exist
        for col in self.COLUMNS:
            if col not in df.columns:
                df.loc[:, col] = "0" if col == "amount" else ""

        # Work on a fresh copy in the expected column order
        df = df.loc[:, self.COLUMNS].copy()

        # Safe, non-chained assignments
        df.loc[:, "amount"] = (
            pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(
                float)
        )
        df.loc[:, "date"] = df["date"].map(NormalizeDateStr)
        return df

    def GetTransactions(self) -> list[Transaction]:
        """Return all transactions as Transaction objects."""
        df = self.GetDataFrame()
        return self.ConvertToTransactionList(df.values.tolist())

    def GetTransactionsBy(self, column_name: str, column_value) -> list[
        Transaction]:
        """Filter by a valid column name and value; return matching
        transactions."""
        if column_name not in self.COLUMNS:
            raise ValueError(
                f"Unknown column '{column_name}'. Expected one of "
                f"{self.COLUMNS}."
            )
        df = self.GetDataFrame()
        rows = df[df[column_name] == column_value].values.tolist()
        return self.ConvertToTransactionList(rows)

    def GetDataFrameInRange(self, start=None, end=None) -> DataFrame:
        """Return a DataFrame filtered by inclusive [start, end] dates."""
        df = self.GetDataFrame().copy()
        if df.empty:
            return df

        s = NormalizeDateStr(str(start)) if start else None
        e = NormalizeDateStr(str(end)) if end else None

        dt = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
        mask = dt.notna()

        if s:
            sdt = pd.to_datetime(s, format="%Y/%m/%d", errors="coerce")
            mask &= dt >= sdt
        if e:
            edt = pd.to_datetime(e, format="%Y/%m/%d", errors="coerce")
            mask &= dt <= edt

        return df.loc[mask].copy()

    # -------------------------
    # Duplicate + persistence
    # -------------------------

    def IsDuplicate(self, tx: Transaction) -> bool:
        """Check for an existing identical transaction (case-insensitive
        fields, amount at 2 decimals)."""
        try:
            df = self.GetDataFrame()
        except Exception:
            return False

        if df is None or df.empty:
            return False

        s_tx = str(tx.transaction).strip().lower()
        s_cat = str(tx.category).strip().lower()
        s_desc = str(tx.description).strip().lower()
        amt2 = round(float(tx.amount), 2)
        d_norm = NormalizeDateStr(str(tx.date))

        mask = (
                df["transaction"].astype(str).str.strip().str.lower().eq(s_tx)
                & df["category"].astype(str).str.strip().str.lower().eq(s_cat)
                & df["description"].astype(str).str.strip().str.lower().eq(
            s_desc)
                & df["amount"].astype(float).round(2).eq(amt2)
                & df["date"].astype(str).eq(d_norm)
        )
        return bool(mask.any())

    def SaveTransaction(self, tx: Transaction) -> None:
        """Append a single transaction in canonical column order."""
        row = [
            str(tx.transaction),
            str(tx.category),
            str(tx.description),
            float(tx.amount),
            NormalizeDateStr(str(tx.date)),
        ]
        with self.CsvPath.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(row)

    def SaveTransactions(self, transactions: Iterable[Transaction]) -> None:
        """Append multiple transactions efficiently."""
        if not transactions:
            return
        with self.CsvPath.open("a", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            for tx in transactions:
                writer.writerow(
                    [
                        str(tx.transaction),
                        str(tx.category),
                        str(tx.description),
                        float(tx.amount),
                        NormalizeDateStr(str(tx.date)),
                    ]
                )

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

    # -------------------------
    # Aggregates for reports
    # -------------------------

    def ExpenseByCategoryData(self, start=None, end=None) -> DataFrame:
        """Return expense totals by category within an optional inclusive
        date range."""
        df = self.GetDataFrameInRange(start, end)
        if df.empty:
            return pd.DataFrame({"category": [], "amount": []})

        t = df["transaction"].astype(str).str.strip().str.lower()
        # Select only columns we need and copy to avoid views
        expenses = df.loc[t.eq("expense"), ["category", "amount"]].copy()
        if expenses.empty:
            return pd.DataFrame({"category": [], "amount": []})

        report = (
            expenses.groupby("category", as_index=False, sort=False)["amount"]
            .sum()
            .copy()
        )
        report.loc[:, "amount"] = report["amount"].astype(float).round(2)
        report = (
            report.sort_values("amount", ascending=False, kind="stable")
            .reset_index(drop=True)
        )
        return report

    def IncomeByCategoryData(self, start=None, end=None) -> DataFrame:
        """Return income totals by category within an optional inclusive date
        range."""
        df = self.GetDataFrameInRange(start, end)
        if df.empty:
            return pd.DataFrame({"category": [], "amount": []})

        t = df["transaction"].astype(str).str.strip().str.lower()
        income = df.loc[t.eq("income"), ["category", "amount"]].copy()
        if income.empty:
            return pd.DataFrame({"category": [], "amount": []})

        report = (
            income.groupby("category", as_index=False, sort=False)["amount"]
            .sum()
            .copy()
        )
        report.loc[:, "amount"] = report["amount"].astype(float).round(2)
        report = (
            report.sort_values("amount", ascending=False, kind="stable")
            .reset_index(drop=True)
        )
        return report

    def AllByCategoryData(self, start=None, end=None) -> pd.DataFrame:
        """Return combined category totals across Income and Expense.

        Output schema: columns ['type', 'category', 'amount'] where 'type' in
        {'Income', 'Expense'}.
        """
        # Build from the already-safe helpers to minimize CoW pitfalls
        exp = self.ExpenseByCategoryData(start, end)
        inc = self.IncomeByCategoryData(start, end)

        frames: list[pd.DataFrame] = []

        if exp is not None and not exp.empty:
            e = exp.copy()
            e.insert(0, "type", "Expense")
            frames.append(e.loc[:, ["type", "category", "amount"]])

        if inc is not None and not inc.empty:
            i = inc.copy()
            i.insert(0, "type", "Income")
            frames.append(i.loc[:, ["type", "category", "amount"]])

        if not frames:
            return pd.DataFrame({"type": [], "category": [], "amount": []})

        # Create a fresh owner DataFrame (copy=True) and then mutate safely
        out = pd.concat(frames, ignore_index=True, copy=True)
        out = out.copy()  # extra safety against view semantics

        # Safe, explicit assignment
        out.loc[:, "type"] = pd.Categorical(
            out["type"], categories=["Income", "Expense"], ordered=True
        )

        # Stable sort: Income first, then Expense; each by amount desc
        out = (
            out.sort_values(["type", "amount"], ascending=[True, False],
                            kind="stable")
            .reset_index(drop=True)
        )
        return out

    def SummaryByMonthData(self) -> DataFrame:
        """Return DataFrame with columns: month ('FullMonth YYYY'), income,
        expense, net."""
        df = self.GetDataFrame().copy()
        df.loc[:, "transaction"] = df["transaction"].astype(
            str).str.strip().str.lower()

        # Build a mask first; then slice; then recompute dt on the sliced frame
        mask = pd.to_datetime(df["date"], format="%Y/%m/%d",
                              errors="coerce").notna()
        df = df.loc[mask].copy()
        dt = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")

        df.loc[:, "__month"] = dt.dt.to_period("M")

        gb = df.groupby(["__month", "transaction"], observed=True)[
            "amount"].sum()
        pt = gb.unstack(fill_value=0.0).copy()

        # Ensure both columns exist; use .loc to avoid chained assignment
        # ambiguity
        for col in ("income", "expense"):
            if col not in pt.columns:
                pt.loc[:, col] = 0.0

        # Normalize dtypes and compute net
        pt = pt.astype({"income": "float64", "expense": "float64"},
                       errors="ignore")
        pt.loc[:, "net"] = pt["income"] - pt["expense"]

        out = pt.reset_index().sort_values("__month").copy()
        out.loc[:, "month"] = out["__month"].dt.to_timestamp().dt.strftime(
            "%B %Y")
        out = out.drop(columns="__month")
        out = out.loc[:, ["month", "income", "expense", "net"]]
        return out
