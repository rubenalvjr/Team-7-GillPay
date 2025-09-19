# AUTHOR: Matthew Bennett
# DATE: 11SEP2025
# PROGRAM: GillPay GUI (Navy + Orange)
# PURPOSE: Minimal Tk/ttk UI that calls GillPayService without changing core logic.
# INPUT: User text fields and buttons.
# PROCESS: Validate inputs, call service layer, refresh table.
# OUTPUT: CSV updates via DAO + on-screen table/summary.
# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.


# gui/app.py
import tkinter as tk
from tkinter import ttk

from src.ui.theme import ApplyTheme
from src.ui.tab_view import ViewTransactionsTab
from src.ui.tab_add import AddTransactionTab
from src.dao.transaction_dao import TransactionDAO


class GillPayApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GillPay")
        self.geometry("820x560")

        # Theme/colors
        self.colors = ApplyTheme(self)

        # Title bar
        title = tk.Frame(self, bg=self.colors["Navy"], height=46)
        title.pack(fill="x")
        tk.Label(
            title,
            text="GillPay",
            fg=self.colors["TextOnDark"],
            bg=self.colors["Navy"],
            font=("Segoe UI", 14, "bold"),
            padx=14,
        ).pack(side="left")

        # Shared DAO
        self.Dao = TransactionDAO()

        # --- Build summary bar BEFORE tabs so labels exist for callbacks ---
        self._BuildSummaryBar()

        # Notebook
        nb = ttk.Notebook(self, style="Gill.TNotebook")
        nb.pack(expand=True, fill="both", padx=10, pady=(10, 6))

        # Tabs
        view_tab = ViewTransactionsTab(nb, self.Dao, on_refresh=self.RefreshSummary)
        add_tab = AddTransactionTab(nb, self.Dao, view_tab)

        nb.add(add_tab, text="Add Transaction")
        nb.add(view_tab, text="View Transactions")

        # Initial fill
        self.RefreshSummary()

    # ---- Summary UI ----
    def _BuildSummaryBar(self):
        bar = tk.Frame(self, bg=self.colors["Navy"])
        bar.pack(fill="x", padx=10, pady=(0, 10))

        f = ("Segoe UI", 10, "bold")
        self.LblIncome = tk.Label(
            bar, text="Income: 0.00", bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f
        )
        self.LblExpense = tk.Label(
            bar, text="Expense: 0.00", bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f
        )
        self.LblNet = tk.Label(
            bar, text="Net: 0.00", bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f
        )

        self.LblIncome.pack(side="left", padx=(12, 16), pady=6)
        self.LblExpense.pack(side="left", padx=(0, 16), pady=6)
        self.LblNet.pack(side="left", padx=(0, 16), pady=6)

    def RefreshSummary(self):
        df = self.Dao.GetDataFrame()
        if df is None or df.empty:
            income = expense = 0.0
        else:
            income = float(df[df["transaction"] == "income"]["amount"].sum())
            expense = float(df[df["transaction"] == "expense"]["amount"].sum())
        net = income - expense

        self.LblIncome.config(text=f"Income: {income:.2f}")
        self.LblExpense.config(text=f"Expense: {expense:.2f}")
        self.LblNet.config(text=f"Net: {net:.2f}")


if __name__ == "__main__":
    GillPayApp().mainloop()
