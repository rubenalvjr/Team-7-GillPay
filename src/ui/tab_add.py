# AUTHOR: Matthew Bennett
# DATE: 27SEP2025
# PROGRAM: Tab Add
# PURPOSE: Renders the tab in the GUI so a user can add transactions

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from tkcalendar import DateEntry
from pathlib import Path

from src.dao.transaction_dao import TransactionDAO
from src.models.transaction import Transaction
from src.categories import AllowedCategoriesForType
from src.dao.category_dao import CategoryDAO
from src.ui.category_manager_dialog import CategoryManagerDialog
from src.ui.theme import COLORS as THEME_COLORS  # optional (for commented hero img)


class AddTransactionTab(ttk.Frame):
    def __init__(self, parent, dao: TransactionDAO, view_tab=None):
        super().__init__(parent, padding=12)
        self.Dao = dao
        self.ViewTab = view_tab
        self.CatDao = CategoryDAO()

        # Common label options for alignment
        label_opts = {"anchor": "e", "width": 15}

        # ----------------
        # Type
        # ----------------
        ttk.Label(self, text="Type:", **label_opts).grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.TypeVar = tk.StringVar(value="Income")
        type_box = ttk.Combobox(self, textvariable=self.TypeVar, state="readonly",
                                values=["Income", "Expense"], width=15)
        type_box.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # Clear selection highlight after choosing a value
        def _clear_combo_selection(event):
            cb = event.widget
            try:
                cb.selection_clear()   # remove highlight
                cb.icursor(tk.END)     # caret to end (cosmetic)
            except Exception:
                pass
        type_box.bind("<<ComboboxSelected>>", _clear_combo_selection, add=True)

        # ----------------
        # Category + Manage…
        # ----------------
        ttk.Label(self, text="Category:", **label_opts).grid(row=1, column=0, sticky="e", padx=6, pady=6)
        self.CatField = ttk.Frame(self)
        self.CatField.grid(row=1, column=1, sticky="w", padx=6, pady=6)
        self.CatField.columnconfigure(0, weight=0)
        self.CatField.columnconfigure(1, weight=1)

        self.CategoryVar = tk.StringVar()
        self.CategoryBox = ttk.Combobox(self.CatField, textvariable=self.CategoryVar,
                                        state="readonly", width=15)
        self.CategoryBox.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.CategoryBox.configure(exportselection=False)  # prevent OS-style reselect

        # Deferred clear so highlight doesn't reappear after Tk updates the entry
        def _clear_combo_selection_now(cb):
            try:
                cb.selection_range(0, 0)
                cb.icursor(tk.END)
            except Exception:
                pass

        def _clear_combo_selection_deferred(event):
            cb = event.widget
            cb.after(0, lambda: _clear_combo_selection_now(cb))

        self.CategoryBox.bind("<<ComboboxSelected>>", _clear_combo_selection_deferred, add=True)
        self.CategoryBox.bind("<FocusIn>", _clear_combo_selection_deferred, add=True)

        ttk.Button(self.CatField, text="Manage Categories", style="Gill.TButton",
                   command=self._OpenCategoryManager).grid(row=0, column=1, sticky="w", padx=(12, 0))

        # Custom category entry (only when "Other" is selected)
        self.CustomCatVar = tk.StringVar()
        self.CustomCatEntry = ttk.Entry(self.CatField, textvariable=self.CustomCatVar, width=30)
        self.CustomCatEntry.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Optional: remove underline/dotbox in combobox dropdown lists
        self.after(0, lambda: self._TweakComboboxDropdown(type_box))
        self.after(0, lambda: self._TweakComboboxDropdown(self.CategoryBox))

        # ----------------
        # Amount
        # ----------------
        ttk.Label(self, text="Amount:", **label_opts).grid(row=2, column=0, sticky="e", padx=6, pady=6)
        self.AmountVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.AmountVar, width=15).grid(row=2, column=1, sticky="w", padx=6, pady=6)

        # ----------------
        # Date
        # ----------------
        ttk.Label(self, text="Date:", **label_opts).grid(row=3, column=0, sticky="e", padx=6, pady=6)
        self.DatePicker = DateEntry(self, year=date.today().year, date_pattern="yyyy/mm/dd",
                                    width=12, state="normal", style="Gill.DateEntry")
        self.DatePicker.grid(row=3, column=1, sticky="w", padx=6, pady=6)

        # Normalize only on Enter (no popup on simple focus changes)
        self.DatePicker.bind("<Return>",   self._NormalizeDatePickerAndBreak, add=True)
        self.DatePicker.bind("<KP_Enter>", self._NormalizeDatePickerAndBreak, add=True)

        # ----------------
        # Description
        # ----------------
        ttk.Label(self, text="Description:", **label_opts).grid(row=4, column=0, sticky="e", padx=6, pady=6)
        self.DescriptionVar = tk.StringVar()
        ttk.Entry(self, textvariable=self.DescriptionVar, width=30).grid(row=4, column=1, sticky="w", padx=6, pady=6)

        # ----------------
        # Buttons
        # ----------------
        row = ttk.Frame(self)
        row.grid(row=5, column=0, columnspan=4, pady=(10, 0))
        ttk.Button(row, text="Save",  style="Gill.TButton", command=self.OnSave).grid(row=0, column=0, padx=6)
        ttk.Button(row, text="Clear", style="Gill.TButton",
                   command=lambda: self.ClearForm(preserve_type=True)).grid(row=0, column=1, padx=6)
        self.columnconfigure(1, weight=1)

        # Keyboard shortcuts
        self.bind_all("<Return>", lambda e: self.OnSave())
        self.bind_all("<Escape>", lambda e: self.ClearForm(preserve_type=True))

        # Init category list & reactive behaviors
        self._SetCategoryOptionsForType(self.TypeVar.get())

        def _on_type_changed(*_):
            self._SetCategoryOptionsForType(self.TypeVar.get())
        self.TypeVar.trace_add("write", _on_type_changed)

        def _on_cat_changed(*_):
            self._ToggleCustomVisibility()
        self.CategoryVar.trace_add("write", _on_cat_changed)

        self._ToggleCustomVisibility()

    # ----------------------------
    # UI helpers
    # ----------------------------
    def _TweakComboboxDropdown(self, cb: ttk.Combobox):
        """
        Remove underline/dotbox in a combobox's popup list on supported Tk builds.
        Safe no-op if structure differs.
        """
        try:
            popdown = cb.nametowidget(cb.tk.eval(f'ttk::combobox::PopdownWindow {cb}'))
            lb = popdown.children['f'].children['lw']
            lb.configure(activestyle='none', selectborderwidth=0, highlightthickness=0)
        except Exception:
            pass

    def _SetCategoryOptionsForType(self, gui_type: str):
        # defaults from helper + user-managed list; ensure 'Other' last
        defaults = [c for c in AllowedCategoriesForType(gui_type) if c.lower() != "other"]
        managed = [c for c in self.CatDao.ListCategoryNames(gui_type) if c.lower() != "other"]

        # merge uniquely while preserving order
        base = defaults[:]
        for n in managed:
            if n not in base:
                base.append(n)
        base.append("Other")

        self.CategoryBox["values"] = base
        current = self.CategoryVar.get()
        self.CategoryVar.set(current if current in base else (base[0] if base else ""))
        self._ToggleCustomVisibility()

    def _OpenCategoryManager(self):
        dlg = CategoryManagerDialog(self, self.CatDao, self.TypeVar.get())
        self.wait_window(dlg)
        if getattr(dlg, "changed", False):
            self._SetCategoryOptionsForType(self.TypeVar.get())

    def _ToggleCustomVisibility(self):
        sel = (self.CategoryVar.get() or "").strip()
        show = sel == "Other"
        if show:
            self.CustomCatEntry.grid()
            self.CustomCatEntry.focus_set()
        else:
            self.CustomCatVar.set("")
            self.CustomCatEntry.grid_remove()

    # ----------------------------
    # Date normalization helpers
    # ----------------------------
    def _NormalizeDatePicker(self) -> bool:
        """
        Accept several human-friendly formats, enforce bounds, normalize to yyyy/mm/dd.
        Returns True if valid; False if invalid.
        """
        raw = (self.DatePicker.get() or "").strip()
        if not raw:
            self.DatePicker.set_date(date.today())
            return True

        fmts = ["%Y/%m/%d", "%Y-%m-%d", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"]
        for fmt in fmts:
            try:
                d = datetime.strptime(raw, fmt).date()
                if d.year < 1900 or d > date.today():
                    return False
                self.DatePicker.set_date(d)
                return True
            except Exception:
                continue
        return False

    def _NormalizeDatePickerAndBreak(self, event=None):
        ok = self._NormalizeDatePicker()
        if not ok:
            messagebox.showerror(
                "Invalid Date",
                "Please enter a valid date (YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, '22 Oct 2025'), "
                "not in the future and not before 1900."
            )
            self.DatePicker.focus_set()
        return "break"

    # ----------------------------
    # Save flow
    # ----------------------------
    def OnSave(self):
        # Ensure the date is valid before reading get_date()
        if not self._NormalizeDatePicker():
            messagebox.showerror(
                "Invalid Date",
                "Please enter a valid date (YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, '22 Oct 2025'), "
                "not in the future and not before 1900."
            )
            self.DatePicker.focus_set()
            return

        txn = self.TypeVar.get().strip().lower()
        sel = (self.CategoryVar.get() or "").strip()
        custom = (self.CustomCatVar.get() or "").strip()
        amt_s = (self.AmountVar.get() or "").strip()
        desc = (self.DescriptionVar.get() or "").strip()
        date_str = self.DatePicker.get_date().strftime("%Y/%m/%d")

        if txn not in ("income", "expense"):
            messagebox.showerror("Invalid Type", 'Type must be "income" or "expense".')
            return

        # Category validation (write-in only when Other is selected)
        allowed = set(AllowedCategoriesForType("Income" if txn == "income" else "Expense"))
        if sel == "Other":
            if not custom:
                messagebox.showerror("Missing Custom Category", "Please enter a custom category.")
                return
            cat_to_save = "Other"
            desc = f"{desc} [{custom}]"
        else:
            if sel not in allowed:
                messagebox.showerror("Invalid Category", "Choose a category from the list.")
                return
            cat_to_save = sel

        # Amount validation
        try:
            amt = Decimal(amt_s)
        except (InvalidOperation, ValueError):
            messagebox.showerror("Invalid Amount", "Amount must be a valid number.")
            return
        if amt <= 0:
            messagebox.showerror("Invalid Amount", "Amount must be greater than zero.")
            return
        amt = amt.quantize(Decimal("0.01"))

        # Description check
        if not desc:
            messagebox.showerror("Missing Description", "Please enter a short description.")
            return

        # Build the transaction AFTER all normalization
        t = Transaction(
            transaction=txn,
            category=cat_to_save,
            description=desc,
            amount=float(amt),
            date=date_str
        )

        # Duplicate check + confirm
        try:
            is_dup = self.Dao.IsDuplicate(t)
        except Exception:
            is_dup = False

        if is_dup:
            proceed = messagebox.askyesno(
                title="Possible Duplicate",
                message="An identical transaction already exists.",
                detail="Type, Category, Description, Amount, and Date all match an existing entry.\n\nDo you want to save it anyway?",
                icon="question",
                default="no",
                parent=self
            )
            if not proceed:
                return

        # Persist
        try:
            self.Dao.SaveTransaction(t)
        except Exception as ex:
            messagebox.showerror("Save Failed", f"Could not save transaction:\n{ex}")
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
