# PROGRAM:     Transaction

# AUTHOR:      Team 7

# PURPOSE:     Core Data Model used for GillPay processes

# INPUT:       Transaction values (Type, Category, Amount, Date)

# PROCESS:     Acts as container of data representing a row of
# data (Transaction)

# OUTPUT:      Transaction Object

# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
# received unauthorized aid on this academic work.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

# src/transaction.py
from dataclasses import dataclass
from typing import Any, Iterable

@dataclass(frozen=True)
class Transaction:
    transaction: str          # "income" | "expense"
    category: str
    description: str
    amount: float
    date: str                 # "YYYY/MM/DD"

    @classmethod
    def from_row(cls, row: Iterable[Any]) -> "Transaction":
        r = list(row)
        return cls(
            transaction=str(r[0]),
            category=str(r[1]),
            description=str(r[2]),
            amount=float(r[3]) if r[3] not in ("", None) else 0.0,
            date=str(r[4]),
        )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Transaction":
        return cls(
            transaction=str(d.get("transaction", "")),
            category=str(d.get("category", "")),
            description=str(d.get("description", "")),
            amount=float(d.get("amount") or 0.0),
            date=str(d.get("date", "")),
        )
