# AUTHOR: Team 7
# DATE: 30SEP2025
# PROGRAM: Charts Tab (Tk)
# PURPOSE: Lightweight GUI tab with four buttons to show GillPay charts (Matplotlib).

from __future__ import annotations

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
    def __init__(self, Master, **Kw):
        super().__init__(Master, **Kw)

        # Layout (controls row + chart host area)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        Controls = ttk.Frame(self)
        Controls.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))

        self.ChartHost = ttk.Frame(self)
        self.ChartHost.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Buttons (use themed style if present; fallback to default)
        BtnStyle = {"style": "Gill.TButton"}
        try:
            # If style not defined, this will no-op; ttk ignores unknown style at runtime.
            ttk.Style().lookup("Gill.TButton", "configure")
        except Exception:
            BtnStyle = {}

        BtnExpCat = ttk.Button(Controls, text="Expense by Category", command=self._OnExpCat, **BtnStyle)
        BtnIncCat = ttk.Button(Controls, text="Income by Category", command=self._OnIncCat, **BtnStyle)
        BtnIE     = ttk.Button(Controls, text="Income vs Expense by Month", command=self._OnIE, **BtnStyle)
        BtnNet    = ttk.Button(Controls, text="Net by Month", command=self._OnNet, **BtnStyle)

        BtnExpCat.pack(side=tk.LEFT, padx=(0, 8))
        BtnIncCat.pack(side=tk.LEFT, padx=8)
        BtnIE.pack(side=tk.LEFT, padx=8)
        BtnNet.pack(side=tk.LEFT, padx=8)

        # Service reference
        self.Service = GillPayService()

        # Note: No default auto-render here. The tab will stay blank until a button is clicked.


    # -------------------------
    # Button handlers / Actions
    # -------------------------
    def _OnExpCat(self):
        try:
            # Expect dict {Category: total}; pass dict directly (builder sorts internally).
            Totals = self.Service.GetExpenseTotalsByCategory()
            Fig = BuildExpenseByCategoryFigure(Totals)
            MountFigureInTk(self.ChartHost, Fig)
        except Exception as Ex:
            self._ShowError(str(Ex))

    def _OnIncCat(self):
        try:
            Totals = self.Service.GetIncomeTotalsByCategory()
            Fig = BuildIncomeByCategoryFigure(Totals)
            MountFigureInTk(self.ChartHost, Fig)
        except Exception as Ex:
            self._ShowError(str(Ex))

    def _OnIE(self):
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

    def _OnNet(self):
        DF = self.Service.TransactionDAO.SummaryByMonthData()
        Data = {
            str(Row["month"]): {"income": 0.0, "expense": 0.0,
                                "net": float(Row["net"])}
            for _, Row in DF.iterrows()
        }
        Fig = BuildNetByMonthFigure(Data)
        MountFigureInTk(self.ChartHost, Fig)

    # -------------------------
    # Error display
    # -------------------------
    def _ShowError(self, Message: str):
        # Clear host
        for Child in self.ChartHost.winfo_children():
            try:
                Child.destroy()
            except Exception:
                pass
        ttk.Label(self.ChartHost, text=f"Error: {Message}").pack(padx=20, pady=20)
