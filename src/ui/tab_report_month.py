# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Tab Report by Month

# PURPOSE: Show "Summary by Month" (Income, Expense, Net) with refresh and
# sorting.

# INPUT: Data from TransactionDAO.

# PROCESS: Load monthly summary and render a sortable table.

# OUTPUT: A Treeview table listing month, income, expense, and net.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Monthly summary report tab (income, expense, net) for GillPay's Tkinter
UI."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from src.dao.transaction_dao import TransactionDAO


class ReportMonthTab(ttk.Frame):
    """Report tab that displays income, expense, and net by month."""

    def __init__(self, parent, dao: TransactionDAO):
        """Initialize controls and load the initial dataset."""
        super().__init__(parent, padding=12)
        self.Dao = dao

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="we", pady=(0, 8))
        ttk.Button(bar, text="Refresh", style="Gill.TButton",
                   command=self.LoadData).grid(row=0, column=0)

        self.Columns = ("month", "income", "expense", "net")
        self.Tree = ttk.Treeview(self, columns=self.Columns, show="headings",
                                 height=16, style="Gill.Treeview")

        headings = {"month": "Month", "income": "Income", "expense": "Expense",
                    "net": "Net"}
        for key, label in headings.items():
            self.Tree.heading(key, text=label,
                              command=lambda c=key: self.SortBy(c, False),
                              anchor="w")
            if key in ("income", "expense", "net"):
                self.Tree.column(key, width=120, anchor="e")
            else:
                self.Tree.column(key, width=160, anchor="w")

        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="")
        self.Tree.grid(row=1, column=0, sticky="nsew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.LoadData()

    def LoadData(self):
        """Load monthly summary from DAO and populate the table."""
        try:
            df = self.Dao.SummaryByMonthData()
        except Exception as ex:
            messagebox.showerror("Load Failed", f"Could not load report:\n{ex}")
            return

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        if df is None or df.empty:
            return

        for c in self.Columns:
            if c not in df.columns:
                return

        for i, (_, row) in enumerate(df.iterrows()):
            values = (
                str(row["month"]),
                f"{float(row['income']):.2f}",
                f"{float(row['expense']):.2f}",
                f"{float(row['net']):.2f}",
            )
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.Tree.insert("", "end", values=values, tags=(tag,))

    def SortBy(self, column: str, descending: bool):
        """Sort rows by the given column; toggle order on subsequent clicks."""
        rows = self.Tree.get_children("")

        def key_func(iid):
            v = self.Tree.set(iid, column)
            if column in ("income", "expense", "net"):
                try:
                    return float(v)
                except Exception:
                    return float("inf")
            if column == "month":
                for fmt in ("%B %Y", "%B"):
                    try:
                        return datetime.strptime(v, fmt)
                    except Exception:
                        pass
                return datetime.max
            return v.lower() if isinstance(v, str) else v

        ordered = sorted(rows, key=key_func, reverse=descending)
        for idx, iid in enumerate(ordered):
            self.Tree.move(iid, "", idx)
            self.Tree.item(iid, tags=("evenrow" if idx % 2 == 0 else "oddrow",))
        self.Tree.heading(column,
                          command=lambda: self.SortBy(column, not descending))
