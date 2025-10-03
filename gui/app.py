# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: GillPay GUI Application

# PURPOSE: Launches the GillPay™ desktop interface and assembles the main window,
# tabs, theme, and summary bar for personal finance tracking.

# INPUT: Reads transactions via TransactionDAO, user actions in the GUI.

# PROCESS: Initializes theme and notebook tabs, displays summary metrics, and
# updates figures on data refresh.

# OUTPUT: A Tkinter-based window with tabs for adding, viewing, reporting, and
# visualizing transactions.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""GillPay GUI launcher and main window composition for the personal finance app."""

import os
os.environ["PANDAS_COPY_ON_WRITE"] = "1"

import tkinter as tk
import sys
from tkinter import ttk
from pathlib import Path

from src.ui.theme import ApplyTheme
from src.ui.tab_view import ViewTransactionsTab
from src.ui.tab_add import AddTransactionTab
from src.ui.tab_report_category import ReportCategoryTab
from src.ui.tab_report_month import ReportMonthTab
from src.dao.transaction_dao import TransactionDAO
from src.ui.tab_charts import ChartsTab


class GillPayApp(tk.Tk):
    """Main Tkinter application for GillPay."""

    def __init__(self):
        """Initialize the window, theme, tabs, and summary bar."""
        super().__init__()
        self.title("GillPay\u2122")
        self.geometry("1024x680")

        def SetAppIcon(win: tk.Tk) -> None:
            """Set the application icon from available image assets."""
            base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
            images = base / "images"

            for name in ("gillpay.ico", "goofy_goldfishes.ico", "app.ico"):
                p = images / name
                if p.exists():
                    try:
                        win.iconbitmap(default=str(p))
                        return
                    except Exception:
                        pass

            for name in ("gillpay_256.png", "goofy_goldfishes_256.png", "gillpay.png"):
                p = images / name
                if p.exists():
                    try:
                        win.iconphoto(True, tk.PhotoImage(file=str(p)))
                        return
                    except Exception:
                        pass

        SetAppIcon(self)

        self.colors = ApplyTheme(self)

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

        try:
            base = Path(__file__).resolve().parents[1]
            images = base / "images"
            for name in ("goofy_goldfishes_128.png", "gillpay.png"):
                p = images / name
                if p.exists():
                    self.LogoSmall = tk.PhotoImage(file=str(p))
                    tk.Label(title, image=self.LogoSmall, bg=self.colors["Navy"]).pack(side="right", padx=24, pady=8)
                    break
        except Exception:
            pass

        self.Dao = TransactionDAO()

        self.BuildSummaryBar()

        self.Notebook = ttk.Notebook(self, style="Gill.TNotebook")
        self.Notebook.pack(expand=True, fill="both", padx=10, pady=(10, 6))

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

        self.RefreshSummary()

    def BuildSummaryBar(self):
        """Create the income, expense, and net summary labels."""
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
        """Update the summary labels using current transaction totals."""
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


def Main():
    """Entry point to launch the GillPay GUI."""
    App = GillPayApp()
    App.mainloop()


if __name__ == "__main__":
    Main()
