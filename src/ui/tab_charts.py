# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Charts Tab (Tk)

# PURPOSE: Lightweight GUI tab with buttons to display GillPay
# charts (Matplotlib).

# INPUT: User clicks on chart buttons; data provided by GillPayService.

# PROCESS: Query service for aggregated data and render themed Matplotlib
# figures.

# OUTPUT: Charts embedded into the tab content area.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


"""Tkinter tab that mounts GillPay charts built with Matplotlib."""

import tkinter as tk
from tkinter import ttk
from src.gillpay_service import GillPayService
from src.ui.charts import (
    BuildExpenseByCategoryFigure,
    BuildIncomeByCategoryFigure,
    BuildIncomeExpenseByMonthFigure,
    BuildNetByMonthFigure,
    MountFigureInTk,
)


class ChartsTab(ttk.Frame):
    """Chart launcher tab hosting four chart buttons and a render area."""

    def __init__(self, Master, **Kw):
        """Initialize layout, buttons, and service reference."""
        super().__init__(Master, **Kw)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        Controls = ttk.Frame(self)
        Controls.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        self.ChartHost = ttk.Frame(self)
        self.ChartHost.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        BtnStyle = {"style": "Gill.TButton"}
        try:
            ttk.Style().lookup("Gill.TButton", "configure")
        except Exception:
            BtnStyle = {}

        BtnExpCat = ttk.Button(Controls, text="Expense by Category",
                               command=self.OnExpCat, **BtnStyle)
        BtnIncCat = ttk.Button(Controls, text="Income by Category",
                               command=self.OnIncCat, **BtnStyle)
        BtnIE = ttk.Button(Controls, text="Income vs Expense by Month",
                           command=self.OnIE, **BtnStyle)
        BtnNet = ttk.Button(Controls, text="Net by Month", command=self.OnNet,
                            **BtnStyle)

        BtnExpCat.pack(side=tk.LEFT, padx=(0, 8))
        BtnIncCat.pack(side=tk.LEFT, padx=8)
        BtnIE.pack(side=tk.LEFT, padx=8)
        BtnNet.pack(side=tk.LEFT, padx=8)

        self.Service = GillPayService()

    # Button handlers / actions

    def OnExpCat(self):
        """Render 'Expense by Category' chart."""
        try:
            Totals = self.Service.GetExpenseTotalsByCategory()
            Fig = BuildExpenseByCategoryFigure(Totals)
            MountFigureInTk(self.ChartHost, Fig)
        except Exception as Ex:
            self.ShowError(str(Ex))

    def OnIncCat(self):
        """Render 'Income by Category' chart."""
        try:
            Totals = self.Service.GetIncomeTotalsByCategory()
            Fig = BuildIncomeByCategoryFigure(Totals)
            MountFigureInTk(self.ChartHost, Fig)
        except Exception as Ex:
            self.ShowError(str(Ex))

    def OnIE(self):
        """Render 'Income vs Expense by Month' chart."""
        DF = self.Service.TransactionDAO.SummaryByMonthData()
        Data = {
            str(Row["month"]): {
                "income": float(Row["income"]),
                "expense": float(Row["expense"]),
                "net": float(Row["net"]),
            }
            for _, Row in DF.iterrows()
        }
        Fig = BuildIncomeExpenseByMonthFigure(Data)
        MountFigureInTk(self.ChartHost, Fig)

    def OnNet(self):
        """Render 'Net by Month' chart."""
        DF = self.Service.TransactionDAO.SummaryByMonthData()
        Data = {
            str(Row["month"]): {"income": 0.0, "expense": 0.0,
                                "net": float(Row["net"])}
            for _, Row in DF.iterrows()
        }
        Fig = BuildNetByMonthFigure(Data)
        MountFigureInTk(self.ChartHost, Fig)

    # Error display

    def ShowError(self, Message: str):
        """Display a simple error label in the chart host area."""
        for Child in self.ChartHost.winfo_children():
            try:
                Child.destroy()
            except Exception:
                pass
        ttk.Label(self.ChartHost, text=f"Error: {Message}").pack(padx=20,
                                                                 pady=20)
