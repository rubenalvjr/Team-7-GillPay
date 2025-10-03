# AUTHOR: Team 7 Goofy Goldfishes

# DATE: 02OCT2025

# PROGRAM: Main

# PURPOSE: Launch GillPay (CLI) and simple visualizations or open the GUI.

# INPUT: User selections via CLI prompts.

# PROCESS: Route actions to service layer; validate inputs; render
# summaries/reports.

# OUTPUT: Saved transactions, printed summaries/reports, or GUI launch.

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# GEN AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

from __future__ import annotations

from datetime import datetime, date
from typing import Dict, Literal, Optional

from src.gillpay_service import GillPayService
from src.models.transaction import Transaction

# Constants for report routing
REPORT_EXP_BY_CAT: Literal["EXP_BY_CAT"] = "EXP_BY_CAT"
REPORT_SUMMARY_BY_MONTH: Literal["SUMMARY_BY_MONTH"] = "SUMMARY_BY_MONTH"

# Validation helpers
ALLOWED_DATE_FORMATS = [
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d %B %Y",
    "%d %b %Y",
]


def TryParseDate(Value: str) -> Optional[datetime]:
    """Return a datetime if *Value* matches any allowed format; otherwise
    None."""
    Clean = (Value or "").strip()
    for Fmt in ALLOWED_DATE_FORMATS:
        try:
            return datetime.strptime(Clean, Fmt)
        except ValueError:
            continue
    return None


def IsValidDate(Value: str) -> bool:
    """Accept several formats; disallow future dates and dates before
    1900-01-01."""
    Dt = TryParseDate(Value)
    if not Dt:
        return False
    D = Dt.date()
    if D.year < 1900:
        return False
    if D > date.today():
        return False
    return True


def PromptAmount() -> float:
    """Prompt until a valid positive numeric amount is entered."""
    while True:
        Raw = input("Transaction Amount (e.g., 12.50): ").strip()
        try:
            Amount = round(float(Raw), 2)
            if Amount <= 0:
                print("Amount must be greater than zero. Please re-enter.")
                continue
            return Amount
        except ValueError:
            print("Amount must be numeric (e.g., 12.50). Please re-enter.")


def PromptDate() -> str:
    """Prompt until a valid date is entered; normalize to YYYY/MM/DD."""
    while True:
        Value = input(
            "Transaction Date (YYYY/MM/DD or '22 Oct 2025'): ").strip()
        Dt = TryParseDate(Value)
        if not Dt:
            print(
                "Unrecognized date format. Try 2025/10/01, 10/01/2025, "
                "or '22 Oct 2025'.")
            continue
        D = Dt.date()
        if D.year < 1900:
            print("Date is too far in the past (before 1900). Please re-enter.")
            continue
        if D > date.today():
            print("Date cannot be in the future. Please re-enter.")
            continue
        return D.strftime("%Y/%m/%d")


def PromptTransactionType() -> str:
    """Prompt until a valid transaction type is entered."""
    while True:
        Value = input("Expense or Income: ").strip().lower()
        if Value in {"expense", "income"}:
            return Value
        print("Please enter 'Expense' or 'Income'.")


def PromptCategory() -> str:
    """Prompt for a non-empty category (free-form)."""
    while True:
        Value = input("Transaction Category: ").strip()
        if Value:
            return Value.lower()
        print("Category cannot be empty.")


def PromptDescription() -> str:
    """Prompt for a non-empty description."""
    while True:
        Value = input("Transaction Description: ").strip()
        if Value:
            return Value
        print("Description cannot be empty.")


# Core CLI actions

def HandleTransaction() -> None:
    """Collect a transaction from the user and persist it via the service."""
    try:
        GillPay = GillPayService()

        print()
        TransactionType = PromptTransactionType()
        TransactionCategory = PromptCategory()
        TransactionDescription = PromptDescription()
        TransactionAmount = PromptAmount()
        TransactionDate = PromptDate()

        NewTransaction = Transaction(
            transaction=TransactionType,
            category=TransactionCategory,
            description=TransactionDescription,
            amount=TransactionAmount,
            date=TransactionDate,
        )

        GillPay.PostTransaction(NewTransaction)
        print("Transaction recorded successfully.")
    except KeyboardInterrupt:
        print("Input cancelled by user.")
    except Exception as Ex:
        print(
            f"An unexpected error occurred while saving the transaction: {Ex}")


def HandleSummary() -> None:
    """Print the account summary (income, expense, net)."""
    try:
        GillPay = GillPayService()
        SummaryData = GillPay.GetTransactionSummary()
        print()
        print(f"{'-' * 5} Account Summary {'-' * 5}")
        print(f"{'Description':10} {'Amount':>10}")
        print(f"{'Income':10} {SummaryData['income']:>10.2f}")
        print(f"{'Expense':10} {SummaryData['expense']:>10.2f}")
        print(f"{'Net':10} {SummaryData['net']:>10.2f}")
    except Exception as Ex:
        print(
            f"An unexpected error occurred while generating the summary: {Ex}")


def HandleReport(ReportType: str) -> None:
    """Display a report. Supported values: EXP_BY_CAT, SUMMARY_BY_MONTH."""
    try:
        GillPay = GillPayService()
        print()
        GillPay.GenerateReport(ReportType)
    except Exception as Ex:
        print(f"An unexpected error occurred while generating the report: {Ex}")


def TryGetCategoryTotals(Service: GillPayService) -> Optional[Dict[str, float]]:
    """Best-effort attempt to obtain expense totals by category from the
    service."""
    try:
        return Service.GetExpenseTotalsByCategory()
    except AttributeError:
        return None
    except Exception:
        return None


def LaunchApp() -> None:
    """Launch the Tk GUI (preferred: gui.app:main(); fallback: run as
    module)."""
    try:
        from gui.app import main as GuiMain
        GuiMain()
        return
    except Exception:
        pass

    try:
        import sys, subprocess
        subprocess.run([sys.executable, "-m", "gui.app"], check=False)
    except Exception as ex:
        print(f"Could not launch GUI: {ex}")


def HandleMatplotlibChart() -> None:
    """Show a simple bar chart of expense totals by category using
    Matplotlib."""
    try:
        import matplotlib.pyplot as plt
    except Exception as Ex:
        print(f"Matplotlib is not available: {Ex}")
        return

    try:
        GillPay = GillPayService()
        TotalsByCategory = GillPay.GetExpenseTotalsByCategory()
    except Exception as Ex:
        print(f"Could not compute category totals: {Ex}")
        return

    if not TotalsByCategory:
        print("No expense data available to chart.")
        return

    Categories = list(TotalsByCategory.keys())
    Amounts = [TotalsByCategory[C] for C in Categories]

    Fig, Ax = plt.subplots()
    Ax.bar(Categories, Amounts)
    Ax.set_title("GillPay Totals by Category")
    Ax.set_ylabel("Amount ($)")
    Ax.set_xlabel("Category")
    Ax.tick_params(axis="x", labelrotation=45)
    Fig.tight_layout()
    plt.show()


# CLI framing

def PrintMenu() -> None:
    """Display the main CLI menu."""
    print(
        "\nHowdy fellow money savers and welcome to the GillPay\u2122 Finance "
        "Tracking Application!\n"
        "\nPlease make a selection from the menu below:\n")
    print("Press 1: Add Transaction")
    print("Press 2: Account Summary")
    print("Press 3: Expense by Category Report")
    print("Press 4: Spending By Month Report")
    print("Press 5: Fancy Chart")
    print("Press 6: Launch GUI")
    print("Press 7: Farewell!")


def main() -> None:
    """Interactive CLI loop for GillPay."""
    GillPayIsRunning = True
    try:
        while GillPayIsRunning:
            PrintMenu()
            try:
                UserChoice = int(input("Action: ").strip())
            except ValueError:
                print(
                    "You entered invalid data. Please enter a number between "
                    "1 and 7.")
                input("Press Enter to continue...")
                continue

            if UserChoice == 1:
                HandleTransaction()
            elif UserChoice == 2:
                HandleSummary()
            elif UserChoice == 3:
                HandleReport(REPORT_EXP_BY_CAT)
            elif UserChoice == 4:
                HandleReport(REPORT_SUMMARY_BY_MONTH)
            elif UserChoice == 5:
                HandleMatplotlibChart()
            elif UserChoice == 6:
                LaunchApp()
            elif UserChoice == 7:
                GillPayIsRunning = False
            else:
                print("Invalid choice, please select value 1 - 7.")
    except KeyboardInterrupt:
        print("Session cancelled by user.")
    finally:
        GillPayLogo()
        print(
            "Thank you for using GillPay\u2122 for your finance tracking "
            "needs!")


# Fun: ASCII logo

def GillPayLogo():
    """Print the GillPay ASCII logo on exit."""
    print("             /`·.¸")
    print("            /¸...¸`:·")
    print("       ¸.·´  ¸   `·.¸.·´)")
    print("      : © ):´; GillPay\u2122  {")
    print("       `·.¸ `·  ¸.·´\\`·¸)")
    print("           `\\\\´´\\¸.·´")


if __name__ == "__main__":
    main()
