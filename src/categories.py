# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: GillPay Category Options

# PURPOSE: Centralized category choices for income and expense transactions,
# ensuring consistent validation and preventing invalid user entries.

# INPUT: Transaction type string ("income" or "expense").

# PROCESS: Map transaction type to allowed categories and provide helpers
# for validation and reporting.

# OUTPUT: Category option lists and validation utilities.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

"""GillPay centralized category definitions and validation helpers."""

CATEGORY_OPTIONS: dict[str, list[str]] = {
    "Income": ["Investments", "Salary", "Other"],
    "Expense": [
        "Bills",
        "Entertainment",
        "Food",
        "Healthcare",
        "Loans",
        "Other",
        "Personal",
        "Savings",
        "Transportation",
    ],
}


def AllowedCategoriesForType(TxType: str) -> list[str]:
    """Return allowed categories for the given transaction type.

    Args:
        TxType: Transaction type ("income" or "expense", case-insensitive).
    Returns:
        List of category strings. Defaults to Expense list if input is invalid.
    """
    key = "Income" if (TxType or "").strip().lower() == "income" else "Expense"
    return CATEGORY_OPTIONS.get(key, [])


def IsValidCategory(TxType: str, Cat: str) -> bool:
    """Check if a category is valid for a given transaction type.

    Args:
        TxType: Transaction type string.
        Cat: Category string to validate.
    Returns:
        True if valid, False otherwise.
    """
    return (Cat or "").strip() in set(AllowedCategoriesForType(TxType))


def BucketCategoryForReport(TxType: str, Cat: str) -> str:
    """Normalize a category for reporting purposes.

    Args:
        TxType: Transaction type string.
        Cat: Category string.
    Returns:
        The category if valid; otherwise "Other Income" (for income)
        or "Other" (for expense).
    """
    gui_key = "Income" if (
                                  TxType or "").strip().lower() == "income" \
        else "Expense"
    allowed = set(CATEGORY_OPTIONS.get(gui_key, []))
    cat = (Cat or "").strip()
    if gui_key == "Income":
        return cat if cat in allowed else "Other Income"
    return cat if cat in allowed else "Other"
