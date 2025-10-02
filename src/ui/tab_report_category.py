# AUTHOR: Matthew Bennett

# DATE: 23SEP2025

# PROGRAM: Tab Report Category

# PURPOSE: Show "Expense by Category" as a table with refresh and sorting.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received unauthorized aid.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.



import tkinter as tk
from tkinter import ttk, messagebox
from src.dao.transaction_dao import TransactionDAO


class ReportCategoryTab(ttk.Frame):
    def __init__(self, parent, dao: TransactionDAO):
        super().__init__(parent, padding=12)
        self.Dao = dao

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="we", pady=(0, 8))
        ttk.Button(bar, text="Refresh", style="Gill.TButton", command=self.LoadData).grid(row=0, column=0)

        self.Columns = ("category", "amount")
        self.Tree = ttk.Treeview(self, columns=self.Columns, show="headings", height=16, style="Gill.Treeview")
        self.Tree.heading("category", text="Category", command=lambda: self.SortBy("category", False), anchor="w")
        self.Tree.heading("amount", text="Amount", command=lambda: self.SortBy("amount", False), anchor="w")
        self.Tree.column("category", width=240, anchor="w")
        self.Tree.column("amount", width=120, anchor="e")
        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="")
        self.Tree.grid(row=1, column=0, sticky="nsew")

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.LoadData()

    def LoadData(self):
        try:
            df = self.Dao.ExpenseByCategoryData()
        except Exception as ex:
            messagebox.showerror("Load Failed", f"Could not load report:\n{ex}")
            return

        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        if df is None or df.empty:
            return

        # Ensure columns exist
        for c in self.Columns:
            if c not in df.columns:
                return  # schema mismatch; silently bail

        for i, (_, row) in enumerate(df.iterrows()):
            values = (str(row["category"]), f"{float(row['amount']):.2f}")
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.Tree.insert("", "end", values=values, tags=(tag,))

    def SortBy(self, column: str, descending: bool):
        rows = self.Tree.get_children("")
        def key_func(iid):
            v = self.Tree.set(iid, column)
            if column == "amount":
                try: return float(v)
                except Exception: return float("inf")
            return v.lower() if isinstance(v, str) else v
        ordered = sorted(rows, key=key_func, reverse=descending)
        for idx, iid in enumerate(ordered):
            self.Tree.move(iid, "", idx)
            self.Tree.item(iid, tags=("evenrow" if idx % 2 == 0 else "oddrow",))
        self.Tree.heading(column, command=lambda: self.SortBy(column, not descending))
