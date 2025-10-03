# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: CategoryDAO

# PURPOSE: Manage income/expense categories stored in a CSV file.

# INPUT: CSV path (optional) and category parameters from callers.

# PROCESS: Initialize default categories, read/write CSV rows, and provide
# list/add/rename/delete operations.

# OUTPUT: Updated CSV and lists of category names for the GUI.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.


"""Data-access object for category management (Income/Expense) backed by CSV."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Dict


class CategoryDAO:
    """Category data access with CSV persistence.

    Columns:
        - type: "Income" or "Expense"
        - name: category display name
        - is_active: "1" (active) or "0" (inactive)
    """

    COLUMNS = ["type", "name", "is_active"]

    DEFAULTS = {
        "Income": [
            "Salary",
            "Bonus",
            "Interest",
            "Dividends",
            "Gifts",
            "Investments",
            "Other",
        ],
        "Expense": [
            "Rent",
            "Utilities",
            "Groceries",
            "Food & Dining",
            "Transportation",
            "Insurance",
            "Entertainment",
            "Healthcare",
            "Education",
            "Investments",
            "Other",
        ],
    }

    def __init__(self, datasource: str | None = None):
        """Create a DAO bound to a CSV file, seeding defaults if absent."""
        if datasource is None:
            repo_root = Path(__file__).resolve().parents[2]
            self.CsvPath = repo_root / "data" / "categories.csv"
        else:
            self.CsvPath = Path(datasource).resolve()
        self.CsvPath.parent.mkdir(parents=True, exist_ok=True)
        if not self.CsvPath.exists():
            with self.CsvPath.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(self.COLUMNS)
                for t, names in self.DEFAULTS.items():
                    for n in names:
                        w.writerow([t, n, "1"])

    def Load(self) -> List[Dict[str, str]]:
        """Read and normalize all category rows from CSV."""
        rows: List[Dict[str, str]] = []
        with self.CsvPath.open("r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append(
                    {
                        "type": (row.get("type") or "").strip().title(),
                        "name": (row.get("name") or "").strip(),
                        "is_active": "1"
                        if (row.get("is_active") or "1").strip() == "1"
                        else "0",
                    }
                )
        return rows

    def Save(self, rows: List[Dict[str, str]]) -> None:
        """Write all category rows to CSV."""
        with self.CsvPath.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=self.COLUMNS)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    def NormalizeType(self, gui_type: str) -> str:
        """Map user/GUI input to canonical 'Income' or 'Expense'."""
        return "Income" if str(gui_type).lower().startswith(
            "inc") else "Expense"

    def ListCategoryNames(self, gui_type: str,
                          include_inactive: bool = False) -> List[str]:
        """Return unique, case-insensitive sorted names for a given type."""
        t = self.NormalizeType(gui_type)
        names: List[str] = []
        for r in self.Load():
            if r["type"] == t and (include_inactive or r["is_active"] == "1"):
                names.append(r["name"])
        seen, out = set(), []
        for n in sorted(names, key=str.casefold):
            if n.casefold() not in seen:
                out.append(n)
                seen.add(n.casefold())
        return out

    def AddCategory(self, gui_type: str, name: str) -> None:
        """Add a new active category or reactivate an existing inactive one."""
        t = self.NormalizeType(gui_type)
        n = (name or "").strip()
        if not n:
            raise ValueError("Category name cannot be empty.")
        if n.lower() == "other":
            raise ValueError("The name 'Other' is reserved.")
        rows = self.Load()
        found_inactive = False
        for r in rows:
            if r["type"] == t and r["name"].casefold() == n.casefold():
                if r["is_active"] == "1":
                    raise ValueError(f"Category '{n}' already exists.")
                r["is_active"] = "1"
                found_inactive = True
        if not found_inactive:
            rows.append({"type": t, "name": n, "is_active": "1"})
        self.Save(rows)

    def RenameCategory(self, gui_type: str, old: str, new: str) -> None:
        """Rename a category within a type, preventing duplicates and 'Other'
        renames."""
        t = self.NormalizeType(gui_type)
        o = (old or "").strip()
        n = (new or "").strip()
        if not o or not n:
            raise ValueError("Both old and new names are required.")
        if o.lower() == "other" or n.lower() == "other":
            raise ValueError("Cannot rename to or from 'Other'.")
        rows = self.Load()
        exists_active = any(
            r["type"] == t and r["name"].casefold() == n.casefold() and r[
                "is_active"] == "1"
            for r in rows
        )
        if exists_active:
            raise ValueError(f"Category '{n}' already exists.")
        changed = False
        for r in rows:
            if r["type"] == t and r["name"].casefold() == o.casefold():
                r["name"] = n
                changed = True
        if not changed:
            raise ValueError(f"Category '{o}' not found.")
        self.Save(rows)

    def DeleteCategory(self, gui_type: str, name: str) -> None:
        """Soft-delete a category (mark inactive) except for 'Other'."""
        t = self.NormalizeType(gui_type)
        n = (name or "").strip()
        if not n:
            return
        if n.lower() == "other":
            raise ValueError("Cannot delete 'Other'.")
        rows = self.Load()
        for r in rows:
            if r["type"] == t and r["name"].casefold() == n.casefold():
                r["is_active"] = "0"
        self.Save(rows)
