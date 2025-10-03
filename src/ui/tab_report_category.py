# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Tab Report Category

# PURPOSE: Show "Expense by Category" as a table with refresh, sorting,
# and inclusive date range.

# INPUT: User-selected start/end dates.

# PROCESS: Query DAO for category totals within the range and render a
# sortable table.

# OUTPUT: A Treeview table and a total amount label.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Report tab showing expense totals by category within a date range."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkcalendar import DateEntry

from src.dao.transaction_dao import TransactionDAO


class ReportCategoryTab(ttk.Frame):
    """Expense-by-category report with date filters and sorting."""

    def __init__(self, parent, dao: TransactionDAO):
        """Initialize pickers, table, and default dates."""
        super().__init__(parent, padding=12)
        self.Dao = dao

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="we", pady=(0, 8))
        bar.columnconfigure(5, weight=1)

        ttk.Label(bar, text="From:").grid(row=0, column=0, padx=(0, 6))
        self.StartPicker = DateEntry(bar, date_pattern="yyyy/mm/dd", width=12,
                                     state="readonly", style="Gill.DateEntry")
        self.StartPicker.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(bar, text="To:").grid(row=0, column=2, padx=(0, 6))
        self.EndPicker = DateEntry(bar, date_pattern="yyyy/mm/dd", width=12,
                                   state="readonly", style="Gill.DateEntry")
        self.EndPicker.grid(row=0, column=3, padx=(0, 12))

        ttk.Button(bar, text="Results", style="Gill.TButton",
                   command=self.LoadData).grid(row=0, column=4, padx=(0, 12))

        self.TotalLabel = ttk.Label(bar, text="Total: $0.00")
        self.TotalLabel.grid(row=0, column=5, sticky="e")

        self.StartPicker.set_date(date.today().replace(day=1))
        self.EndPicker.set_date(date.today())

        self.Columns = ("category", "amount")
        self.Tree = ttk.Treeview(self, columns=self.Columns, show="headings",
                                 height=16, style="Gill.Treeview")
        self.Tree.heading("category", text="Category",
                          command=lambda: self.SortBy("category", False),
                          anchor="w")
        self.Tree.heading("amount", text="Amount",
                          command=lambda: self.SortBy("amount", False),
                          anchor="e")
        self.Tree.column("category", width=240, anchor="w")
        self.Tree.column("amount", width=120, anchor="e")
        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="")
        self.Tree.grid(row=1, column=0, sticky="nsew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.LoadData()
        self.after(0, self.StabilizePickers)

    def LoadData(self):
        """Fetch data for the selected range and populate the table and
        total."""
        try:
            start = self.StartPicker.get_date().strftime("%Y/%m/%d")
            end = self.EndPicker.get_date().strftime("%Y/%m/%d")
        except Exception as ex:
            messagebox.showerror("Invalid Date",
                                 f"Please choose valid dates.\n{ex}")
            return

        if start > end:
            start, end = end, start

        try:
            df = self.Dao.ExpenseByCategoryData(start, end)
        except Exception as ex:
            messagebox.showerror("Load Failed", f"Could not load report:\n{ex}")
            return

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        if df is None or df.empty:
            self.TotalLabel.config(text="Total: $0.00")
            return

        for c in self.Columns:
            if c not in df.columns:
                messagebox.showerror("Schema Error",
                                     "Report data missing expected columns.")
                return

        for i, (_, row) in enumerate(df.iterrows()):
            values = (str(row["category"]), f"{float(row['amount']):.2f}")
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.Tree.insert("", "end", values=values, tags=(tag,))

        total = float(df["amount"].sum())
        self.TotalLabel.config(text=f"Total: ${total:,.2f}")

    def SortBy(self, column: str, descending: bool):
        """Sort the table by a given column; toggle order on subsequent
        clicks."""
        rows = self.Tree.get_children("")

        def key_func(iid):
            v = self.Tree.set(iid, column)
            if column == "amount":
                try:
                    return float(v)
                except Exception:
                    return float("inf")
            return v.lower() if isinstance(v, str) else v

        ordered = sorted(rows, key=key_func, reverse=descending)
        for idx, iid in enumerate(ordered):
            self.Tree.move(iid, "", idx)
            self.Tree.item(iid, tags=("evenrow" if idx % 2 == 0 else "oddrow",))
        self.Tree.heading(column,
                          command=lambda: self.SortBy(column, not descending))

    def StabilizePickers(self):
        """One-time tweak after widget realization to stabilize DateEntry
        popups."""
        try:
            self.update_idletasks()
            for w in (self.StartPicker, self.EndPicker):
                w.configure(state="normal")
                w.configure(state="readonly")
        except Exception:
            pass
