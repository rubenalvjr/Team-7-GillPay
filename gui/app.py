# gui/app.py
import os
os.environ["PANDAS_COPY_ON_WRITE"] = "1"   # set BEFORE any pandas-using imports

import tkinter as tk
from tkinter import ttk
from src.ui.theme import ApplyTheme
from src.ui.tab_view import ViewTransactionsTab
from src.ui.tab_add import AddTransactionTab
from src.ui.tab_report_category import ReportCategoryTab
from src.ui.tab_report_month import ReportMonthTab
from src.dao.transaction_dao import TransactionDAO
from src.ui.tab_charts import ChartsTab


class GillPayApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GillPay")
        self.geometry("1024x680")

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

        # Build summary bar BEFORE tabs so labels exist for callbacks
        self._BuildSummaryBar()

        # Notebook
        self.Notebook = ttk.Notebook(self, style="Gill.TNotebook")
        self.Notebook.pack(expand=True, fill="both", padx=10, pady=(10, 6))

        # Tabs
        view_tab = ViewTransactionsTab(self.Notebook, self.Dao, on_refresh=self.RefreshSummary)
        add_tab = AddTransactionTab(self.Notebook, self.Dao, view_tab)
        report_cat_tab = ReportCategoryTab(self.Notebook, self.Dao)
        report_month_tab = ReportMonthTab(self.Notebook, self.Dao)
        charts_tab = ChartsTab(self.Notebook)

        self.Notebook.add(add_tab, text="Add Transaction")
        self.Notebook.add(view_tab, text="View Transactions")
        self.Notebook.add(report_cat_tab, text="Report: Category")
        self.Notebook.add(report_month_tab, text="Report: Month")
        self.Notebook.add(charts_tab, text="Visualizations")

        # Initial fill
        self.RefreshSummary()

    def _BuildSummaryBar(self):
        bar = tk.Frame(self, bg=self.colors["Navy"])
        bar.pack(fill="x", padx=10, pady=(0, 10))

        f = ("Segoe UI", 10, "bold")
        self.LblIncome = tk.Label(bar, text="Income: 0.00",  bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f)
        self.LblExpense = tk.Label(bar, text="Expense: 0.00", bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f)
        self.LblNet = tk.Label(bar, text="Net: 0.00",       bg=self.colors["Navy"], fg=self.colors["TextOnDark"], font=f)

        self.LblIncome.pack(side="left", padx=(12, 16), pady=6)
        self.LblExpense.pack(side="left", padx=(0, 16), pady=6)
        self.LblNet.pack(side="left", padx=(0, 16), pady=6)

    def RefreshSummary(self, df=None):
        try:
            if df is None:
                df = self.Dao.GetDataFrame()
        except Exception:
            income = expense = 0.0
        else:
            t = df["transaction"].astype(str).str.lower()
            income = float(df.loc[t.eq("income"),  "amount"].sum())
            expense = float(df.loc[t.eq("expense"), "amount"].sum())

        net = income - expense
        self.LblIncome.config(text=f"Income: ${income:,.2f}")
        self.LblExpense.config(text=f"Expense: ${expense:,.2f}")
        self.LblNet.config(text=f"Net: ${net:,.2f}")


def main():
    App = GillPayApp()
    App.mainloop()


if __name__ == "__main__":
    main()
