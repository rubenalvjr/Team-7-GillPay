# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Transaction

# PURPOSE: Core data model used for GillPay processes.

# INPUT: Transaction values (type, category, description, amount, date).

# PROCESS: Encapsulates values representing a single transaction row.

# OUTPUT: Transaction object instances.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""Transaction dataclass representing a single financial record."""

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class Transaction:
    """Immutable data container for a GillPay transaction."""

    transaction: str
    category: str
    description: str
    amount: float
    date: str

    @classmethod
    def FromRow(cls, row: Iterable[Any]) -> "Transaction":
        """Create a Transaction from a row-like iterable."""
        r = list(row)
        return cls(
            transaction=str(r[0]),
            category=str(r[1]),
            description=str(r[2]),
            amount=float(r[3]) if r[3] not in ("", None) else 0.0,
            date=str(r[4]),
        )

    @classmethod
    def FromDict(cls, d: dict[str, Any]) -> "Transaction":
        """Create a Transaction from a dict-like mapping."""
        return cls(
            transaction=str(d.get("transaction", "")),
            category=str(d.get("category", "")),
            description=str(d.get("description", "")),
            amount=float(d.get("amount") or 0.0),
            date=str(d.get("date", "")),
        )
