# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

# src/ui/tab_view.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from src.dao.transaction_dao import TransactionDAO

class ViewTransactionsTab(ttk.Frame):
    def __init__(self, parent, dao: TransactionDAO, on_refresh=None):
        super().__init__(parent, padding=12)
        self.Dao = dao
        # callback to update summary in the app
        self.OnRefresh = on_refresh

        # Top bar
        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="w", pady=(0, 8))
        ttk.Button(bar, text="Refresh", style="Gill.TButton", command=self.LoadData).grid(row=0, column=0, padx=(0, 8))

        # Table
        self.Columns = ("transaction", "category", "description", "amount", "date")
        self.Tree = ttk.Treeview(self, columns=self.Columns, show="headings", height=16, style="Gill.Treeview")

        headings = {
            "transaction": "Type",
            "category": "Category",
            "description": "Description",
            "amount": "Amount",
            "date": "Date",
        }
        for key, label in headings.items():
            self.Tree.heading(key, text=label, command=lambda c=key: self.SortBy(c, False), anchor="w")

            if key == "amount":
                self.Tree.column(key, width=110, anchor="e")  # right-align amount
            elif key == "description":
                self.Tree.column(key, width=260, anchor="w")
            else:
                self.Tree.column(key, width=140, anchor="w")

        # Zebra rows (Treeview bg comes from theme)
        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="#FFFFFF")

        # Scrollbars
        xscroll = ttk.Scrollbar(self, orient="horizontal", command=self.Tree.xview)
        yscroll = ttk.Scrollbar(self, orient="vertical", command=self.Tree.yview)
        self.Tree.configure(xscrollcommand=xscroll.set, yscrollcommand=yscroll.set)

        self.Tree.grid(row=1, column=0, sticky="nsew")
        yscroll.grid(row=1, column=1, sticky="ns")
        xscroll.grid(row=2, column=0, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Initial load
        self.LoadData()

    def LoadData(self):
        """Load data from DAO into the Treeview; then notify parent for summary refresh."""
        try:
            df = self.Dao.GetDataFrame()
        except Exception as ex:
            messagebox.showerror("Load Failed", f"Could not load transactions:\n{ex}")
            return

        # Clear table
        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        if df is None or df.empty:
            if callable(self.OnRefresh):
                self.OnRefresh()
            return

        # Ensure columns exist/order (defensive)
        expected = list(self.Columns)
        for c in expected:
            if c not in df.columns:
                df[c] = "" if c != "amount" else 0.0
        df = df[expected]

        # Insert rows; amount as 2 decimals
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

        # Let the app recompute its summary totals now that rows are current
        if callable(self.OnRefresh):
            self.OnRefresh()

    def SortBy(self, column: str, descending: bool):
        """Sort the Treeview rows; keeps numeric sort for Amount."""
        data = [(self.Tree.set(k, column), k) for k in self.Tree.get_children("")]
        if column == "amount":
            try:
                data = [(float(v), k) for v, k in data]
            except ValueError:
                # fallback to string sort if any malformed values
                data = [(self.Tree.set(k, column), k) for k in self.Tree.get_children("")]
        data.sort(reverse=descending)
        for idx, (_, k) in enumerate(data):
            self.Tree.move(k, "", idx)
        self.Tree.heading(column, command=lambda: self.SortBy(column, not descending))
