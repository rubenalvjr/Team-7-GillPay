# AUTHOR: Matthew Bennett

# DATE: 27SEP2025

# PROGRAM: Tab Add

# PURPOSE: Renders the tab in the GUI so a user can add transactions

# INPUT: Takes user input/requests from GillPay GUI

# PROCESS: Validates request data from GillPay GUI and interacts with the data access layer

# OUTPUT: Persists a new transaction and refreshes the View tab if present

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.


# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, InvalidOperation
from tkcalendar import DateEntry
from src.dao.transaction_dao import TransactionDAO
from src.models.transaction import Transaction
from src.categories import AllowedCategoriesForType


class AddTransactionTab(ttk.Frame):
    def __init__(self, parent, dao: TransactionDAO, view_tab=None):
        super().__init__(parent, padding=12)
        self.Dao = dao
        self.ViewTab = view_tab

        # Common label options for alignment
        label_opts = {"anchor": "e", "width": 15}

        # Type
        ttk.Label(self, text="Type:", **label_opts).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.TypeVar = tk.StringVar(value="Income")
        type_box = ttk.Combobox(self, textvariable=self.TypeVar, state="readonly", values=["Income", "Expense"], width=15)
        type_box.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Category
        ttk.Label(self, text="Category:", **label_opts).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.CatField = ttk.Frame(self)
        self.CatField.grid(row=1, column=1, sticky="w", padx=6, pady=6)
        self.CatField.columnconfigure(1, weight=1)

        self.CategoryVar = tk.StringVar()
        self.CategoryBox = ttk.Combobox(self.CatField, textvariable=self.CategoryVar, state="readonly", width=15)
        self.CategoryBox.grid(row=0, column=0, columnspan=2, sticky="w")

        # Custom category entry (hidden unless Other is selected)
        self.CustomCatVar = tk.StringVar()
        self.CustomCatEntry = ttk.Entry(self.CatField, textvariable=self.CustomCatVar, width=30)
        self.CustomCatEntry.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Amount
        ttk.Label(self, text="Amount:", **label_opts).grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.AmountVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.AmountVar, width=15).grid(row=2, column=1, sticky="w", padx=6, pady=6)

        # Date
        ttk.Label(self, text="Date:", **label_opts).grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.DatePicker = DateEntry(self, year=date.today().year, date_pattern="yyyy/mm/dd", width=12)
        self.DatePicker.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        # Description
        ttk.Label(self, text="Description:", **label_opts).grid(row=4, column=0, sticky="e", padx=6, pady=6)
        self.DescriptionVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.DescriptionVar, width=30).grid(row=4, column=1, sticky="w", padx=6, pady=6)

        # Buttons
        row = ttk.Frame(self)
        row.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(row, text="Save", style="Gill.TButton", command=self.OnSave).grid(row=0, column=0, padx=6)
        ttk.Button(row, text="Clear", style="Gill.TButton", command=lambda: self.ClearForm(preserve_type=True)).grid(row=0, column=1, padx=6)
        self.columnconfigure(1, weight=1)

        # Keyboard shortcuts
        self.bind_all("<Return>", lambda e: self.OnSave())
        self.bind_all("<Escape>", lambda e: self.ClearForm(preserve_type=True))

        # Init lists + reactive behaviors
        self._SetCategoryOptionsForType(self.TypeVar.get())

        def _on_type_changed(*_):
            self._SetCategoryOptionsForType(self.TypeVar.get())
        self.TypeVar.trace_add("write", _on_type_changed)

        def _on_cat_changed(*_):
            self._ToggleCustomVisibility()
        self.CategoryVar.trace_add("write", _on_cat_changed)

        self._ToggleCustomVisibility()

    def _SetCategoryOptionsForType(self, gui_type: str):
        opts = AllowedCategoriesForType(gui_type)
        self.CategoryBox["values"] = opts
        self.CategoryVar.set(opts[0] if opts else "")
        self._ToggleCustomVisibility()

    def _ToggleCustomVisibility(self):
        sel = (self.CategoryVar.get() or "").strip()
        show = sel == "Other"
        if show:
            self.CustomCatEntry.grid()
            self.CustomCatEntry.focus_set()
        else:
            self.CustomCatVar.set("")
            self.CustomCatEntry.grid_remove()

    def OnSave(self):
        txn = self.TypeVar.get().strip().lower()
        sel = (self.CategoryVar.get() or "").strip()
        custom = (self.CustomCatVar.get() or "").strip()
        amt_s = (self.AmountVar.get() or "").strip()
        desc = (self.DescriptionVar.get() or "").strip()
        date_str = self.DatePicker.get_date().strftime("%Y/%m/%d")

        if txn not in ("income", "expense"):
            messagebox.showerror("Invalid Type",'Type must be "income" or "expense".')
            return

        # Category validation: allow write-in only when Other is selected.
        # Save "Other" as the category, and append the user's label to the description.
        allowed = set(AllowedCategoriesForType(
            "Income" if txn == "income" else "Expense"))
        if sel == "Other":
            if not custom:
                messagebox.showerror("Missing Custom Category","Please enter a custom category.")
                return
            cat_to_save = "Other"
            desc = f"{desc} [{custom}]"
        else:
            if sel not in allowed:
                messagebox.showerror("Invalid Category","Choose a category from the list.")
                return
            cat_to_save = sel

        # Amount validation using Decimal
        try:
            amt = Decimal(amt_s)
        except (InvalidOperation, ValueError):
            messagebox.showerror("Invalid Amount","Amount must be a valid number.")
            return

        if amt <= 0:
            messagebox.showerror("Invalid Amount","Amount must be greater than zero.")
            return

        # store as two decimals (no negative sign for expenses)
        amt = amt.quantize(Decimal("0.01"))

        # Description check
        if not desc:
            messagebox.showerror("Missing Description","Please enter a short description.")
            return

        t = Transaction(
            transaction=txn,
            category=cat_to_save,
            description=desc,
            amount=float(amt),
            date=date_str
        )
        try:
            self.Dao.SaveTransaction(t)
        except Exception as ex:
            messagebox.showerror("Save Failed",f"Could not save transaction:\n{ex}")
            return

        self.ClearForm(preserve_type=True)
        if self.ViewTab:
            self.ViewTab.LoadData()

    def ClearForm(self, preserve_type: bool = False):
        current_type = self.TypeVar.get()
        if not preserve_type:
            current_type = "Income"
        self.TypeVar.set(current_type)
        self._SetCategoryOptionsForType(current_type)
        self.AmountVar.set("")
        self.DatePicker.set_date(date.today())
        self.DescriptionVar.set("")
        self.CustomCatVar.set("")
        self._ToggleCustomVisibility()