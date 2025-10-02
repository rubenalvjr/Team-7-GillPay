# AUTHOR: Matthew Bennett

# DATE: 30SEP2025

# PROGRAM: GillPay Category Options

# PURPOSE: Centralize allowed categories for GUI/CLI/reports to limit users
# choice and prevent potential errors from selection type or human error in
# data entries.

# INPUT:   Transaction Type ("income" or "expense").

# PROCESS: Provide allowed category choices based on type.

# OUTPUT:  Lists of category strings and validation helper.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

# GUI labels use Title Case to match what users expect.
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
        "Transportation"
    ],
}

def AllowedCategoriesForType(TxType: str) -> list[str]:
    """
    Return allowed categories given a transaction type string.
    Accepts 'income'/'expense' (any case). Falls back to Expense list.
    """
    key = "Income" if (TxType or "").strip().lower() == "income" else "Expense"
    return CATEGORY_OPTIONS.get(key, [])

def IsValidCategory(TxType: str, Cat: str) -> bool:
    """
    True if Cat is an allowed category for the given transaction type.
    """
    return (Cat or "").strip() in set(AllowedCategoriesForType(TxType))

def BucketCategoryForReport(TxType: str, Cat: str) -> str:
    """
    For reporting: if Cat is not one of the standard categories for the type,
    bucket it into 'Other Income' (for income) or 'Other' (for expense).
    """
    gui_key = "Income" if (TxType or "").strip().lower() == "income" else "Expense"
    allowed = set(CATEGORY_OPTIONS.get(gui_key, []))
    cat = (Cat or "").strip()
    if gui_key == "Income":
        return cat if cat in allowed else "Other Income"
    else:
        return cat if cat in allowed else "Other"
