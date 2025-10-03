# AUTHOR: Team 7
# DATE: 02OCT2025
# PROGRAM: Category Manager Dialog
# PURPOSE: Modal to Add / Rename / Delete (archive) categories with app-themed UI,
#          including an in-dialog Income/Expense selector.

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from src.dao.category_dao import CategoryDAO
from src.ui.theme import COLORS as THEME_COLORS


class CategoryManagerDialog(tk.Toplevel):
    def __init__(self, parent, dao: CategoryDAO, gui_type: str):
        super().__init__(parent)

        # Basics
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.dao = dao
        self.changed = False

        # App colors (fallback to theme constants if not exposed on the root)
        try:
            self.colors = getattr(parent.winfo_toplevel(), "colors", THEME_COLORS)
        except Exception:
            self.colors = THEME_COLORS

        # Dialog-scoped theme
        self._apply_dialog_theme()

        # ---------- Header: Type selector ----------
        hdr = ttk.Frame(self, padding=(12, 12, 12, 0), style="Dialog.TFrame")
        hdr.grid(row=0, column=0, sticky="we")
        hdr.columnconfigure(2, weight=1)

        ttk.Label(hdr, text="Type:", style="Dialog.TLabel").grid(row=0, column=0, padx=(0, 6))
        self.TypeVar = tk.StringVar(
            value=("Income" if str(gui_type).lower().startswith("inc") else "Expense")
        )
        self.TypeBox = ttk.Combobox(
            hdr, textvariable=self.TypeVar, state="readonly",
            values=["Income", "Expense"], width=12
        )
        self.TypeBox.grid(row=0, column=1, padx=(0, 12))
        self.TypeBox.bind("<<ComboboxSelected>>", self._on_type_changed)

        # Dynamic title reflects selection
        self._set_title()

        # ---------- Body ----------
        body = ttk.Frame(self, padding=(12, 10), style="Dialog.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(body, text="Categories", style="Dialog.TLabel")\
            .grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.List = tk.Listbox(body, height=12)
        self.List.grid(row=1, column=0, sticky="nsew")
        body.rowconfigure(1, weight=1)
        body.columnconfigure(0, weight=1)
        self.List.configure(
            bg=self.colors["White"],
            fg=self.colors["TextOnLight"],
            selectbackground=self.colors["Selection"],
            selectforeground=self.colors["TextOnLight"],
            highlightthickness=1,
            highlightbackground=self.colors["Border"],
            highlightcolor=self.colors["Orange"],
            relief="flat",
            activestyle="none",
        )

        # Buttons
        btns = ttk.Frame(body, style="Dialog.TFrame")
        btns.grid(row=2, column=0, pady=(10, 0), sticky="e")
        ttk.Button(btns, text="Add",    style="Gill.TButton", command=self._on_add).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Rename", style="Gill.TButton", command=self._on_rename).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Delete", style="Gill.TButton", command=self._on_delete).grid(row=0, column=2, padx=6)
        ttk.Button(btns, text="Close",  style="Gill.TButton", command=self._on_close).grid(row=0, column=3, padx=6)

        # Populate + UX niceties
        self._load()
        self._center(parent)
        self.List.focus_set()
        self.bind("<Escape>", lambda e: self._on_close())

    # ---------- Theme helpers ----------

    def _apply_dialog_theme(self):
        """Scope dialog visuals so we don't affect global theme."""
        self.configure(bg=self.colors["Surface"])
        s = ttk.Style(self)
        s.configure("Dialog.TFrame", background=self.colors["Surface"])
        s.configure("Dialog.TLabel", background=self.colors["Surface"], foreground=self.colors["TextOnLight"])

    # ---------- Data helpers ----------

    def _current_type(self) -> str:
        # Return exactly "Income" or "Expense"
        return "Income" if str(self.TypeVar.get()).lower().startswith("inc") else "Expense"

    def _load(self):
        self.List.delete(0, tk.END)
        names = self.dao.ListCategoryNames(self._current_type())
        for n in names:
            if n.lower() != "other":  # keep 'Other' reserved; not editable here
                self.List.insert(tk.END, n)

    def _selected(self):
        try:
            return self.List.get(self.List.curselection()[0])
        except Exception:
            return None

    def _set_title(self):
        self.title(f"Manage Categories — {self._current_type()}")

    # ---------- Actions ----------

    def _on_type_changed(self, _evt=None):
        self._set_title()
        self._load()

    def _on_add(self):
        t = self._current_type()
        n = simpledialog.askstring("Add Category", f"New {t} category name:", parent=self)
        if not n:
            return
        try:
            self.dao.AddCategory(t, n)
            self.changed = True
            self._load()
        except Exception as ex:
            messagebox.showerror("Add Failed", str(ex), parent=self)

    def _on_rename(self):
        t = self._current_type()
        old = self._selected()
        if not old:
            messagebox.showinfo("Rename", "Select a category to rename.", parent=self)
            return
        new = simpledialog.askstring("Rename Category", f"Rename '{old}' to:", initialvalue=old, parent=self)
        if not new or new == old:
            return
        try:
            self.dao.RenameCategory(t, old, new)
            self.changed = True
            self._load()
        except Exception as ex:
            messagebox.showerror("Rename Failed", str(ex), parent=self)

    def _on_delete(self):
        t = self._current_type()
        n = self._selected()
        if not n:
            messagebox.showinfo("Delete", "Select a category to delete.", parent=self)
            return
        if messagebox.askyesno("Confirm Delete", f"Remove '{n}' from {t} categories?", parent=self):
            try:
                self.dao.DeleteCategory(t, n)  # soft delete (archives)
                self.changed = True
                self._load()
            except Exception as ex:
                messagebox.showerror("Delete Failed", str(ex), parent=self)

    def _on_close(self):
        self.destroy()

    # ---------- Layout ----------

    def _center(self, parent):
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
            py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        except Exception:
            px = py = 100
        self.geometry(f"+{px}+{py}")
