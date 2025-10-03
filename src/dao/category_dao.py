# src/dao/category_dao.py
from __future__ import annotations
import csv
from pathlib import Path
from typing import List, Dict

class CategoryDAO:
    COLUMNS = ["type", "name", "is_active"]  # type: Income/Expense, is_active: "1"/"0"

    DEFAULTS = {
        "Income": [
            "Salary", "Bonus", "Interest", "Dividends", "Gifts", "Investments", "Other"
        ],
        "Expense": [
            "Rent", "Utilities", "Groceries", "Food & Dining", "Transportation",
            "Insurance", "Entertainment", "Healthcare", "Education", "Investments", "Other"
        ],
    }

    def __init__(self, datasource: str | None = None):
        if datasource is None:
            repo_root = Path(__file__).resolve().parents[2]
            self.csv_path = repo_root / "data" / "categories.csv"
        else:
            self.csv_path = Path(datasource).resolve()
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.csv_path.exists():
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                w = csv.writer(f); w.writerow(self.COLUMNS)
                for t, names in self.DEFAULTS.items():
                    for n in names:
                        w.writerow([t, n, "1"])

    # ---------- helpers ----------
    def _load(self) -> List[Dict[str, str]]:
        rows: List[Dict[str, str]] = []
        with self.csv_path.open("r", newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                rows.append({
                    "type": (row.get("type") or "").strip().title(),
                    "name": (row.get("name") or "").strip(),
                    "is_active": "1" if (row.get("is_active") or "1").strip() == "1" else "0",
                })
        return rows

    def _save(self, rows: List[Dict[str, str]]) -> None:
        with self.csv_path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=self.COLUMNS)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    def _norm_type(self, gui_type: str) -> str:
        return "Income" if str(gui_type).lower().startswith("inc") else "Expense"

    # ---------- queries ----------
    def ListCategoryNames(self, gui_type: str, include_inactive: bool = False) -> List[str]:
        t = self._norm_type(gui_type)
        names = []
        for r in self._load():
            if r["type"] == t and (include_inactive or r["is_active"] == "1"):
                names.append(r["name"])
        # unique + stable case-insensitive sort
        seen, out = set(), []
        for n in sorted(names, key=str.casefold):
            if n.casefold() not in seen:
                out.append(n); seen.add(n.casefold())
        return out

    # ---------- mutations ----------
    def AddCategory(self, gui_type: str, name: str) -> None:
        t = self._norm_type(gui_type)
        n = (name or "").strip()
        if not n: raise ValueError("Category name cannot be empty.")
        if n.lower() == "other": raise ValueError("The name 'Other' is reserved.")
        rows = self._load()
        # reactivate if it exists inactive
        found_inactive = False
        for r in rows:
            if r["type"] == t and r["name"].casefold() == n.casefold():
                if r["is_active"] == "1":
                    raise ValueError(f"Category '{n}' already exists.")
                r["is_active"] = "1"; found_inactive = True
        if not found_inactive:
            rows.append({"type": t, "name": n, "is_active": "1"})
        self._save(rows)

    def RenameCategory(self, gui_type: str, old: str, new: str) -> None:
        t = self._norm_type(gui_type)
        o = (old or "").strip(); n = (new or "").strip()
        if not o or not n: raise ValueError("Both old and new names are required.")
        if o.lower() == "other" or n.lower() == "other":
            raise ValueError("Cannot rename to or from 'Other'.")
        rows = self._load()
        exists_active = any(r["type"] == t and r["name"].casefold() == n.casefold() and r["is_active"] == "1" for r in rows)
        if exists_active: raise ValueError(f"Category '{n}' already exists.")
        changed = False
        for r in rows:
            if r["type"] == t and r["name"].casefold() == o.casefold():
                r["name"] = n; changed = True
        if not changed: raise ValueError(f"Category '{o}' not found.")
        self._save(rows)

    def DeleteCategory(self, gui_type: str, name: str) -> None:
        t = self._norm_type(gui_type)
        n = (name or "").strip()
        if not n: return
        if n.lower() == "other": raise ValueError("Cannot delete 'Other'.")
        rows = self._load()
        for r in rows:
            if r["type"] == t and r["name"].casefold() == n.casefold():
                r["is_active"] = "0"
        self._save(rows)
