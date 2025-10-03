# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: TransactionDAO

# PURPOSE: Data access layer for GillPay that reads and writes transactions to CSV.

# INPUT: CSV path (optional) and transaction parameters from callers.

# PROCESS: Load data with Pandas for querying; append rows with csv.writer; normalize dates.

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


DateInFormats = ("%Y/%m/%d", "%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y")


def NormalizeDateStr(s: str) -> str:
    """Normalize many common date strings to 'YYYY/MM/DD' or return empty string for falsy."""
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
    """DAO with a single CSV schema: ['transaction', 'category', 'description', 'amount', 'date']."""

    COLUMNS: list[str] = ["transaction", "category", "description", "amount", "date"]

    def __init__(self, datasource: str | None = None):
        """Bind to <repo>/data/gillpay_data.csv unless a custom path is provided; ensure header exists."""
        if datasource is None:
            repo_root = Path(__file__).resolve().parents[2]
            self.CsvPath = repo_root / "data" / "gillpay_data.csv"
        else:
            self.CsvPath = Path(datasource).resolve()

        self.CsvPath.parent.mkdir(parents=True, exist_ok=True)
        if not self.CsvPath.exists():
            self.CsvPath.write_text(",".join(self.COLUMNS) + "\n", encoding="utf-8")

        self.Datasource = str(self.CsvPath)

    def GetDataFrame(self) -> DataFrame:
        """Load all transactions as a DataFrame with normalized types and date format."""
        try:
            df = pd.read_csv(self.Datasource, dtype=str)
        except FileNotFoundError:
            df = pd.DataFrame(columns=self.COLUMNS)

        for col in self.COLUMNS:
            if col not in df.columns:
                df[col] = "0" if col == "amount" else ""

        df = df[self.COLUMNS].copy()
        df.loc[:, "amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).astype(float)
        df.loc[:, "date"] = df["date"].map(NormalizeDateStr)
        return df

    def GetTransactions(self) -> list[Transaction]:
        """Return all transactions as Transaction objects."""
        df = self.GetDataFrame()
        return self.ConvertToTransactionList(df.values.tolist())

    def GetTransactionsBy(self, column_name: str, column_value) -> list[Transaction]:
        """Filter by a valid column name and value; return matching transactions."""
        if column_name not in self.COLUMNS:
            raise ValueError(f"Unknown column '{column_name}'. Expected one of {self.COLUMNS}.")
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

    def IsDuplicate(self, tx: Transaction) -> bool:
        """Check for an existing identical transaction (case-insensitive fields, amount at 2 decimals)."""
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
            & df["description"].astype(str).str.strip().str.lower().eq(s_desc)
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

    def ExpenseByCategoryData(self, start=None, end=None) -> DataFrame:
        """Return expense totals by category within an optional inclusive date range."""
        df = self.GetDataFrameInRange(start, end)
        if df.empty:
            return pd.DataFrame({"category": [], "amount": []})

        t = df["transaction"].astype(str).str.strip().str.lower()
        expenses = df.loc[t.eq("expense")].copy()
        if expenses.empty:
            return pd.DataFrame({"category": [], "amount": []})

        report = expenses.groupby("category")["amount"].sum().reset_index().copy()
        report.loc[:, "amount"] = report["amount"].astype(float).round(2)
        return report.sort_values("amount", ascending=False)

    def SummaryByMonthData(self) -> DataFrame:
        """Return DataFrame with columns: month ('FullMonth YYYY'), income, expense, net."""
        df = self.GetDataFrame().copy()
        df.loc[:, "transaction"] = df["transaction"].astype(str).str.strip().str.lower()

        dt = pd.to_datetime(df["date"], format="%Y/%m/%d", errors="coerce")
        df = df.loc[dt.notna()].copy()
        df.loc[:, "__month"] = dt.dt.to_period("M")

        gb = df.groupby(["__month", "transaction"], observed=True)["amount"].sum()
        pt = gb.unstack(fill_value=0.0)

        for col in ("income", "expense"):
            if col not in pt.columns:
                pt[col] = 0.0
        pt = pt.astype({"income": "float64", "expense": "float64"}, errors="ignore")

        pt.loc[:, "net"] = pt["income"] - pt["expense"]

        out = pt.reset_index().sort_values("__month").copy()
        out.loc[:, "month"] = out["__month"].dt.to_timestamp().dt.strftime("%B %Y")
        out = out.drop(columns="__month")
        out = out.loc[:, ["month", "income", "expense", "net"]]
        return out
