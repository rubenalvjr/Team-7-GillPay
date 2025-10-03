# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Category Manager Dialog

# PURPOSE: Modal to add, rename, and delete categories with app-themed UI,
# including an in-dialog Income/Expense selector.

# INPUT: GUI events and user input; CategoryDAO instance.

# PROCESS: Load categories by type, perform add/rename/delete via DAO,
# and reflect changes in the list.

# OUTPUT: Updated categories persisted via DAO and reflected in the dialog.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Dialog for managing Income/Expense categories in GillPay."""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

from src.dao.category_dao import CategoryDAO
from src.ui.theme import COLORS as THEME_COLORS


class CategoryManagerDialog(tk.Toplevel):
    """Modal dialog to manage categories for the selected type."""

    def __init__(self, parent, dao: CategoryDAO, gui_type: str):
        """Initialize dialog, theme, widgets, and load current categories."""
        super().__init__(parent)
        self.transient(parent)
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.OnClose)

        self.dao = dao
        self.changed = False

        try:
            self.colors = getattr(parent.winfo_toplevel(), "colors",
                                  THEME_COLORS)
        except Exception:
            self.colors = THEME_COLORS

        self.ApplyDialogTheme()

        hdr = ttk.Frame(self, padding=(12, 12, 12, 0), style="Dialog.TFrame")
        hdr.grid(row=0, column=0, sticky="we")
        hdr.columnconfigure(2, weight=1)

        ttk.Label(hdr, text="Type:", style="Dialog.TLabel").grid(row=0,
                                                                 column=0,
                                                                 padx=(0, 6))
        self.TypeVar = tk.StringVar(
            value=("Income" if str(gui_type).lower().startswith(
                "inc") else "Expense")
        )
        self.TypeBox = ttk.Combobox(
            hdr, textvariable=self.TypeVar, state="readonly",
            values=["Income", "Expense"], width=12
        )
        self.TypeBox.grid(row=0, column=1, padx=(0, 12))
        self.TypeBox.bind("<<ComboboxSelected>>", self.OnTypeChanged)

        self.SetTitle()

        body = ttk.Frame(self, padding=(12, 10), style="Dialog.TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(body, text="Categories", style="Dialog.TLabel").grid(row=0,
                                                                       column=0,
                                                                       sticky="w",
                                                                       pady=(0,
                                                                             6))

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

        btns = ttk.Frame(body, style="Dialog.TFrame")
        btns.grid(row=2, column=0, pady=(10, 0), sticky="e")
        ttk.Button(btns, text="Add", style="Gill.TButton",
                   command=self.OnAdd).grid(row=0, column=0, padx=6)
        ttk.Button(btns, text="Rename", style="Gill.TButton",
                   command=self.OnRename).grid(row=0, column=1, padx=6)
        ttk.Button(btns, text="Delete", style="Gill.TButton",
                   command=self.OnDelete).grid(row=0, column=2, padx=6)
        ttk.Button(btns, text="Close", style="Gill.TButton",
                   command=self.OnClose).grid(row=0, column=3, padx=6)

        self.Load()
        self.Center(parent)
        self.List.focus_set()
        self.bind("<Escape>", lambda e: self.OnClose())

    # Theme helpers

    def ApplyDialogTheme(self):
        """Apply dialog-scoped styles without changing the global theme."""
        self.configure(bg=self.colors["Surface"])
        s = ttk.Style(self)
        s.configure("Dialog.TFrame", background=self.colors["Surface"])
        s.configure("Dialog.TLabel", background=self.colors["Surface"],
                    foreground=self.colors["TextOnLight"])

    # Data helpers

    def CurrentType(self) -> str:
        """Return the current type as 'Income' or 'Expense'."""
        return "Income" if str(self.TypeVar.get()).lower().startswith(
            "inc") else "Expense"

    def Load(self):
        """Populate the listbox with active category names for the selected
        type."""
        self.List.delete(0, tk.END)
        names = self.dao.ListCategoryNames(self.CurrentType())
        for n in names:
            if n.lower() != "other":
                self.List.insert(tk.END, n)

    def Selected(self):
        """Return the currently selected category name or None."""
        try:
            return self.List.get(self.List.curselection()[0])
        except Exception:
            return None

    def SetTitle(self):
        """Set the dialog title based on the current type."""
        self.title(f"Manage Categories - {self.CurrentType()}")

    # Actions

    def OnTypeChanged(self, _evt=None):
        """Handle type selection changes."""
        self.SetTitle()
        self.Load()

    def OnAdd(self):
        """Prompt for and add a new category."""
        t = self.CurrentType()
        n = simpledialog.askstring("Add Category", f"New {t} category name:",
                                   parent=self)
        if not n:
            return
        try:
            self.dao.AddCategory(t, n)
            self.changed = True
            self.Load()
        except Exception as ex:
            messagebox.showerror("Add Failed", str(ex), parent=self)

    def OnRename(self):
        """Prompt for and rename the selected category."""
        t = self.CurrentType()
        old = self.Selected()
        if not old:
            messagebox.showinfo("Rename", "Select a category to rename.",
                                parent=self)
            return
        new = simpledialog.askstring("Rename Category", f"Rename '{old}' to:",
                                     initialvalue=old, parent=self)
        if not new or new == old:
            return
        try:
            self.dao.RenameCategory(t, old, new)
            self.changed = True
            self.Load()
        except Exception as ex:
            messagebox.showerror("Rename Failed", str(ex), parent=self)

    def OnDelete(self):
        """Soft-delete the selected category (archive)."""
        t = self.CurrentType()
        n = self.Selected()
        if not n:
            messagebox.showinfo("Delete", "Select a category to delete.",
                                parent=self)
            return
        if messagebox.askyesno("Confirm Delete",
                               f"Remove '{n}' from {t} categories?",
                               parent=self):
            try:
                self.dao.DeleteCategory(t, n)
                self.changed = True
                self.Load()
            except Exception as ex:
                messagebox.showerror("Delete Failed", str(ex), parent=self)

    def OnClose(self):
        """Close the dialog."""
        self.destroy()

    # Layout

    def Center(self, parent):
        """Center the dialog over the parent window."""
        self.update_idletasks()
        try:
            px = parent.winfo_rootx() + (parent.winfo_width() // 2) - (
                        self.winfo_width() // 2)
            py = parent.winfo_rooty() + (parent.winfo_height() // 2) - (
                        self.winfo_height() // 2)
        except Exception:
            px = py = 100
        self.geometry(f"+{px}+{py}")
