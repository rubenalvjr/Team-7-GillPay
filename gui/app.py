# gui/app.py
import os
os.environ["PANDAS_COPY_ON_WRITE"] = "1"   # set BEFORE any pandas-using imports

import tkinter as tk
import sys
from tkinter import ttk
from src.ui.theme import ApplyTheme
from src.ui.tab_view import ViewTransactionsTab
from src.ui.tab_add import AddTransactionTab
from src.ui.tab_report_category import ReportCategoryTab
from src.ui.tab_report_month import ReportMonthTab
from src.dao.transaction_dao import TransactionDAO
from src.ui.tab_charts import ChartsTab
from pathlib import Path


class GillPayApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GillPay\u2122")
        self.geometry("1024x680")



        def _set_app_icon(win: tk.Tk) -> None:
            # Resolve your project root (parent of /gui)
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
            images = base / "images"

            # Try ICO first (best on Windows)
            for name in ("gillpay.ico", "goofy_goldfishes.ico", "app.ico"):
                p = images / name
                if p.exists():
                    try:
                        win.iconbitmap(default=str(p))
                        return
                    except Exception:
                        pass

            # Fallback to PNG (cross-platform)
            for name in ("gillpay_256.png", "goofy_goldfishes_256.png", "gillpay.png"):
                p = images / name
                if p.exists():
                    try:
                        win.iconphoto(True, tk.PhotoImage(file=str(p)))
                        return
                    except Exception:
                        pass

        _set_app_icon(self)

        # Theme/colors
        self.colors = ApplyTheme(self)

        # Title bar
        title = tk.Frame(self, bg=self.colors["Navy"], height=10)
        title.pack(fill="x")
        tk.Label(
            title,
            text="\nWelcome to GillPay\u2122  Your Personal Financial Tracking Application",
            fg=self.colors["Orange"],
            bg=self.colors["Navy"],
            font=("Segoe UI", 16, "bold"),
            padx=24,
        ).pack(side="left")

        # Right-aligned logo in the title bar
        try:
            base = Path(__file__).resolve().parents[1]  # project root
            images = base / "images"
            # pick a crisp size you have in /images
            for name in ("goofy_goldfishes_128.png", "gillpay.png"):
                p = images / name
                if p.exists():
                    self.LogoSmall = tk.PhotoImage(file=str(p))  # keep a ref on self
                    tk.Label(title, image=self.LogoSmall, bg=self.colors["Navy"]).pack(side="right", padx=24, pady=8)
                    break
        except Exception:
            pass

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
        bar.pack(fill="x", padx=10, pady=(20, 20))

        f = ("Segoe UI", 12, "bold")
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
