# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Tab View

# PURPOSE: Provide transaction filtering, sorting, and display for GillPay.

# INPUT: User-selected filters (type, category) and DAO data.

# PROCESS: Load data, apply filters, and render the table; update summary via
# callback.

# OUTPUT: A Treeview with transactions and a refreshed summary bar.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


"""Transactions table tab with filter controls and sorting."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.dao.category_dao import CategoryDAO
from src.dao.transaction_dao import TransactionDAO


class ViewTransactionsTab(ttk.Frame):
    """Tab to view, filter, and sort transactions."""

    def __init__(self, parent, dao: TransactionDAO, on_refresh=None):
        """Initialize filters, table, and initial data load."""
        super().__init__(parent, padding=12)
        self.Dao = dao
        self.CatDao = CategoryDAO()
        self.OnRefresh = on_refresh

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="we", pady=(0, 8))
        bar.columnconfigure(5, weight=1)

        ttk.Label(bar, text="Type:").grid(row=0, column=0, sticky="e",
                                          padx=(0, 6))
        self.TypeFilterVar = tk.StringVar(value="All")
        self.TypeFilter = ttk.Combobox(
            bar,
            textvariable=self.TypeFilterVar,
            state="readonly",
            values=["All", "Income", "Expense"],
            width=12,
        )
        self.TypeFilter.grid(row=0, column=1, sticky="w", padx=(0, 12))

        ttk.Label(bar, text="Category:").grid(row=0, column=2, sticky="e",
                                              padx=(0, 6))
        self.CategoryFilterVar = tk.StringVar(value="All")
        self.CategoryFilter = ttk.Combobox(bar,
                                           textvariable=self.CategoryFilterVar,
                                           state="readonly", width=22)
        self.CategoryFilter.grid(row=0, column=3, sticky="w", padx=(0, 12))

        self.RefreshCategoryFilter()
        self.TypeFilterVar.trace_add("write",
                                     lambda *_: self.OnTypeFilterChanged())
        self.CategoryFilterVar.trace_add("write", lambda *_: self.LoadData())

        ttk.Button(bar, text="Refresh", style="Gill.TButton",
                   command=self.LoadData).grid(row=0, column=4, padx=(0, 8))

        self.Columns = ("transaction", "category", "description", "amount",
                        "date")
        self.Tree = ttk.Treeview(self, columns=self.Columns, show="headings",
                                 height=16, style="Gill.Treeview")

        headings = {
            "transaction": "Type",
            "category": "Category",
            "description": "Description",
            "amount": "Amount",
            "date": "Date",
        }

        for key, label in headings.items():
            self.Tree.heading(key, text=label,
                              command=lambda c=key: self.SortBy(c, False),
                              anchor="w")
            if key == "amount":
                self.Tree.column(key, width=110, anchor="e")
            elif key == "description":
                self.Tree.column(key, width=260, anchor="w")
            else:
                self.Tree.column(key, width=140, anchor="w")

        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="")
        self.Tree.grid(row=1, column=0, sticky="nsew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.LoadData()

    def OnTypeFilterChanged(self):
        """When Type changes, rebuild Category filter list and reload table."""
        self.RefreshCategoryFilter()
        self.LoadData()

    def RefreshCategoryFilter(self):
        """Set Category options based on current Type filter; include 'All' first."""
        typ = (self.TypeFilterVar.get() or "All").strip()
        if typ == "All":
            income = self.CatDao.ListCategoryNames("Income")
            expense = self.CatDao.ListCategoryNames("Expense")
            merged = sorted(set(income) | set(expense), key=str.casefold)
            vals = ["All"] + merged
        else:
            vals = ["All"] + self.CatDao.ListCategoryNames(typ)

        self.CategoryFilter["values"] = vals
        cur = self.CategoryFilterVar.get()
        self.CategoryFilterVar.set(cur if cur in vals else "All")

    def LoadData(self):
        """Load DataFrame from DAO, apply filters, and render into the Treeview."""
        try:
            df = self.Dao.GetDataFrame()
        except Exception as ex:
            messagebox.showerror("Load Failed",
                                 f"Could not load transactions:\n{ex}")
            return

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        if df is None or df.empty:
            if callable(self.OnRefresh):
                self.OnRefresh(df)
            return

        expected = list(self.Columns)
        for c in expected:
            if c not in df.columns:
                df[c] = "" if c != "amount" else 0.0
        df = df.loc[:, expected].copy()

        typ = (self.TypeFilterVar.get() or "All").strip()
        cat = (self.CategoryFilterVar.get() or "All").strip()
        if typ != "All":
            df = df[df["transaction"].str.lower() == typ.lower()]
        if cat != "All":
            df = df[df["category"] == cat]

        for i, (_, row) in enumerate(df.iterrows()):
            values = (
                str(row["transaction"]),
                str(row["category"]),
                str(row["description"]),
                f"{float(row['amount']):.2f}",
                str(row["date"]),
            )
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.Tree.insert("", "end", values=values, tags=(tag,))

        if callable(self.OnRefresh):
            self.OnRefresh(df)

    def SortBy(self, column: str, descending: bool):
        """Sort the Treeview rows. Numeric for Amount, chronological for
        Date."""
        rows = self.Tree.get_children("")

        def key_func(item_id):
            v = self.Tree.set(item_id, column)
            if column == "amount":
                try:
                    return float(v)
                except Exception:
                    return float("inf")
            if column == "date":
                try:
                    return datetime.strptime(v, "%Y/%m/%d")
                except Exception:
                    return datetime.max
            return v.lower() if isinstance(v, str) else v

        sorted_rows = sorted(rows, key=key_func, reverse=descending)
        for idx, iid in enumerate(sorted_rows):
            self.Tree.move(iid, "", idx)
            self.Tree.item(iid, tags=("evenrow" if idx % 2 == 0 else "oddrow",))
        self.Tree.heading(column,
                          command=lambda: self.SortBy(column, not descending))
