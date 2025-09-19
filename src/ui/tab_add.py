# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from tkcalendar import DateEntry
from src.dao.transaction_dao import TransactionDAO
from src.models.transaction import Transaction

class AddTransactionTab(ttk.Frame):
    def __init__(self, parent, dao: TransactionDAO, view_tab=None):
        super().__init__(parent, padding=12)
        self.Dao = dao; self.ViewTab = view_tab

        ttk.Label(self, text="Type:").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.TypeVar = tk.StringVar(value="Income")
        ttk.Combobox(self, textvariable=self.TypeVar, state="readonly",
                     values=["Income","Expense"], width=18).grid(row=0, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(self, text="Category:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.CategoryVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.CategoryVar, width=22).grid(row=1, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(self, text="Amount:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.AmountVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.AmountVar, width=22).grid(row=2, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(self, text="Date:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.DatePicker = DateEntry(self, year=date.today().year, date_pattern="yyyy/mm/dd", width=19)
        self.DatePicker.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        ttk.Label(self, text="Description:").grid(row=4, column=0, sticky="e", padx=6, pady=6)
        self.DescriptionVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.DescriptionVar, width=30).grid(row=4, column=1, sticky="w", padx=6, pady=6)

        row = ttk.Frame(self); row.grid(row=5, column=0, columnspan=2, pady=(10,0))
        ttk.Button(row, text="Save", style="Gill.TButton", command=self.OnSave).grid(row=0, column=0, padx=6)
        ttk.Button(row, text="Clear", style="Gill.TButton", command=self.ClearForm).grid(row=0, column=1, padx=6)
        self.columnconfigure(1, weight=1)

    def OnSave(self):
        txn = self.TypeVar.get().strip().lower()
        cat = self.CategoryVar.get().strip()
        amt_s = self.AmountVar.get().strip()
        desc = self.DescriptionVar.get().strip()
        date_str = self.DatePicker.get_date().strftime("%Y/%m/%d")

        if txn not in ("income","expense"):
            messagebox.showerror("Invalid Type", 'Type must be "income" or "expense".'); return
        if not cat:
            messagebox.showerror("Missing Category", "Please enter a category."); return
        try: amt = float(amt_s)
        except ValueError:
            messagebox.showerror("Invalid Amount", "Amount must be a number."); return

        t = Transaction(transaction=txn, category=cat, description=desc, amount=amt, date=date_str)
        try: self.Dao.SaveTransaction(t)
        except Exception as ex:
            messagebox.showerror("Save Failed", f"Could not save transaction:\n{ex}"); return

        self.ClearForm()
        if self.ViewTab: self.ViewTab.LoadData()

    def ClearForm(self):
        self.TypeVar.set("Income"); self.CategoryVar.set(""); self.AmountVar.set("")
        self.DatePicker.set_date(date.today()); self.DescriptionVar.set("")
