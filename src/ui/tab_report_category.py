# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Tab Report Category

# PURPOSE: Show category totals as a table with refresh, sorting,
# and inclusive date range.

# INPUT: User-selected type (Expense/Income/All) and start/end dates.

# PROCESS: Query DAO and render a sortable table.

# OUTPUT: A Treeview table and a total amount label.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


"""Category totals report tab (Expense/Income/All) with a sortable table and
inclusive date range. Manual date entry accepts multiple formats and is
normalized via `NormalizeDateStr` to YYYY/MM/DD.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from tkcalendar import DateEntry
from src.dao.transaction_dao import TransactionDAO, NormalizeDateStr


class ReportCategoryTab(ttk.Frame):
    """Tkinter frame showing totals by category with type/date filters and
    sorting."""

    def __init__(self, parent, dao: TransactionDAO):
        """Build UI, bind events, set defaults, and load initial data."""
        super().__init__(parent, padding=12)
        self.Dao = dao

        bar = ttk.Frame(self)
        bar.grid(row=0, column=0, sticky="we", pady=(0, 8))
        bar.columnconfigure(7, weight=1)

        # Type (All/Expense/Income)
        ttk.Label(bar, text="Type:").grid(row=0, column=0, padx=(0, 6))
        self.TypeVar = tk.StringVar(value="All")
        self.TypeBox = ttk.Combobox(
            bar, textvariable=self.TypeVar, state="readonly",
            values=["All", "Expense", "Income"], width=12
        )
        self.TypeBox.grid(row=0, column=1, padx=(0, 12))
        self.TypeBox.bind("<<ComboboxSelected>>", lambda e: self.LoadData())

        # From / To pickers
        ttk.Label(bar, text="From:").grid(row=0, column=2, padx=(0, 6))
        self.StartPicker = DateEntry(bar, date_pattern="yyyy/mm/dd", width=12,
                                     state="normal", style="Gill.DateEntry")
        self.StartPicker.grid(row=0, column=3, padx=(0, 12))

        ttk.Label(bar, text="To:").grid(row=0, column=4, padx=(0, 6))
        self.EndPicker = DateEntry(bar, date_pattern="yyyy/mm/dd", width=12,
                                   state="normal", style="Gill.DateEntry")
        self.EndPicker.grid(row=0, column=5, padx=(0, 12))

        # Enter to refresh (normalize first)
        self.StartPicker.bind("<Return>",
                              lambda e: (self.OnReturn(self.StartPicker),
                                         "break"), add=True)
        self.StartPicker.bind("<KP_Enter>",
                              lambda e: (self.OnReturn(self.StartPicker),
                                         "break"), add=True)
        self.EndPicker.bind("<Return>",
                            lambda e: (self.OnReturn(self.EndPicker), "break"),
                            add=True)
        self.EndPicker.bind("<KP_Enter>",
                            lambda e: (self.OnReturn(self.EndPicker), "break"),
                            add=True)

        ttk.Button(bar, text="Results", style="Gill.TButton",
                   command=self.OnResultsClick).grid(row=0, column=6,
                                                     padx=(0, 12))

        self.TotalLabel = ttk.Label(bar, text="Total: $0.00")
        self.TotalLabel.grid(row=0, column=7, sticky="e")

        # Defaults
        self.StartPicker.set_date(date.today().replace(day=1))
        self.EndPicker.set_date(date.today())

        # Table (hide 'type' unless showing All)
        self.ColumnsAll = ("type", "category", "amount")
        self.Tree = ttk.Treeview(self, columns=self.ColumnsAll, show="headings",
                                 height=16, style="Gill.Treeview")
        self.Tree.heading("type", text="Type",
                          command=lambda: self.SortBy("type", False),
                          anchor="w")
        self.Tree.heading("category", text="Category",
                          command=lambda: self.SortBy("category", False),
                          anchor="w")
        self.Tree.heading("amount", text="Amount",
                          command=lambda: self.SortBy("amount", False),
                          anchor="e")
        self.Tree.column("type", width=0, minwidth=0, stretch=False, anchor="w")
        self.Tree.column("category", width=240, anchor="w")
        self.Tree.column("amount", width=120, anchor="e")
        self.Tree.tag_configure("oddrow", background="#F6F9FC")
        self.Tree.tag_configure("evenrow", background="")
        self.Tree.grid(row=1, column=0, sticky="nsew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        self.LoadData()

    # ---- Date normalization helpers ----

    def _normalize_picker(self, picker: DateEntry) -> bool:
        """Parse/normalize a DateEntry's text; set picker or show error.
        Returns True on success."""
        raw = (picker.get() or "").strip()
        if not raw:
            picker.set_date(date.today())
            return True
        norm = NormalizeDateStr(raw)
        try:
            d = datetime.strptime(norm, "%Y/%m/%d").date()
        except Exception:
            messagebox.showerror(
                "Invalid Date",
                "Accepted: YYYY/MM/DD, YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY, "
                "'05 Oct 2025', '05 October 2025'."
            )
            picker.focus_set()
            try:
                picker.selection_range(0, tk.END)
            except Exception:
                pass
            return False
        picker.set_date(d)
        return True

    def _normalize_both_or_abort(self) -> bool:
        """Normalize Start/End; return False if either fails."""
        return self._normalize_picker(
            self.StartPicker) and self._normalize_picker(self.EndPicker)

    def OnReturn(self, picker: DateEntry):
        """Enter handler for a picker: normalize then reload."""
        if self._normalize_picker(picker) and self._normalize_both_or_abort():
            self.LoadData()

    def OnResultsClick(self):
        """Normalize both pickers and reload."""
        if self._normalize_both_or_abort():
            self.LoadData()

    # ---- Core load & table ----

    def _ShowTypeColumn(self, show: bool):
        """Show/hide the 'Type' column."""
        if show:
            self.Tree.column("type", width=120, minwidth=80, stretch=True,
                             anchor="w")
            self.Tree.heading("type", text="Type")
        else:
            self.Tree.column("type", width=0, minwidth=0, stretch=False,
                             anchor="w")
            self.Tree.heading("type", text="")

    def LoadData(self):
        """Fetch data for current type/date range and render table + totals."""
        try:
            start = self.StartPicker.get_date().strftime("%Y/%m/%d")
            end = self.EndPicker.get_date().strftime("%Y/%m/%d")
        except Exception as ex:
            messagebox.showerror("Invalid Date",
                                 f"Please choose valid dates.\n{ex}")
            return

        if start > end:
            start, end = end, start

        typ = (self.TypeVar.get() or "Expense").strip()
        try:
            if typ == "Expense":
                df = self.Dao.ExpenseByCategoryData(start, end)
            elif typ == "Income":
                df = self.Dao.IncomeByCategoryData(start, end)
            else:
                df = self.Dao.AllByCategoryData(start, end)
        except Exception as ex:
            messagebox.showerror("Load Failed", f"Could not load report:\n{ex}")
            return

        # Clear table
        for iid in self.Tree.get_children():
            self.Tree.delete(iid)

        # Toggle 'Type' column
        self._ShowTypeColumn(typ == "All")

        if df is None or df.empty:
            self.TotalLabel.config(
                text="Income: $0.00   Expense: $0.00   Net: $0.00" if typ ==
                                                                      "All"
                else "Total: $0.00"
            )
            return

        # Schema check
        expected = {"category", "amount"} | (
            {"type"} if typ == "All" else set())
        if any(c not in df.columns for c in expected):
            messagebox.showerror("Schema Error",
                                 "Report data missing expected columns.")
            return

        # Populate
        if typ == "All":
            for i, (_, row) in enumerate(df.iterrows()):
                values = (str(row["type"]), str(row["category"]),
                          f"{float(row['amount']):.2f}")
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.Tree.insert("", "end", values=values, tags=(tag,))
            inc_total = float(df.loc[df["type"] == "Income", "amount"].sum())
            exp_total = float(df.loc[df["type"] == "Expense", "amount"].sum())
            net = inc_total - exp_total
            self.TotalLabel.config(
                text=f"Income: ${inc_total:,.2f}   Expense: $"
                     f"{exp_total:,.2f}   Net: ${net:,.2f}"
            )
        else:
            for i, (_, row) in enumerate(df.iterrows()):
                values = (typ, str(row["category"]),
                          f"{float(row['amount']):.2f}")  # typ in hidden col
                tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.Tree.insert("", "end", values=values, tags=(tag,))
            total = float(df["amount"].sum())
            self.TotalLabel.config(text=f"Total: ${total:,.2f}")

    def SortBy(self, column: str, descending: bool):
        """Sort the Treeview by column; toggles asc/desc."""
        rows = self.Tree.get_children("")

        def key_func(iid):
            v = self.Tree.set(iid, column)
            if column == "amount":
                try:
                    return float(v)
                except Exception:
                    return float("inf")
            return v.lower() if isinstance(v, str) else v

        ordered = sorted(rows, key=key_func, reverse=descending)
        for idx, iid in enumerate(ordered):
            self.Tree.move(iid, "", idx)
            self.Tree.item(iid, tags=("evenrow" if idx % 2 == 0 else "oddrow",))
        self.Tree.heading(column,
                          command=lambda: self.SortBy(column, not descending))
