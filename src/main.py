# AUTHOR: Team 7

# DATE: 28SEP2025

# PROGRAM: Main

# PURPOSE: Launches GillPay application (CLI) and light fun visualizations

# INPUT: Asks for user input to create a transaction, view reports, or open a turtle chart

# PROCESS:
# User selects 1 then inputs data to capture transaction
# User selects 2 then account summary info is displayed
# User selects 3 then Expense by Category Report is displayed
# User selects 4 then Spending By Month Report is displayed
# User selects 5 then Turtle chart opens (fun)
# User selects 6 then application is closed (prints ASCII fish)

# OUTPUT: Successful transaction creation, account summary, reports, or a turtle chart

# HONOR CODE: On my honor, as an Aggie, I have neither given nor received
# unauthorized aid on this academic work.

# Gen AI: In keeping with my commitment to leverage advanced technology for
# enhanced efficiency and accuracy in my work, I use generative artificial
# intelligence tools to assist in writing my Python code.

from __future__ import annotations

from datetime import datetime
from typing import Dict, Literal, Optional

from src.gillpay_service import GillPayService
from src.models.transaction import Transaction


# Constants for report routing
REPORT_EXP_BY_CAT: Literal["EXP_BY_CAT"] = "EXP_BY_CAT"
REPORT_SUMMARY_BY_MONTH: Literal["SUMMARY_BY_MONTH"] = "SUMMARY_BY_MONTH"


# ----------------------------
# Utility: Validation helpers
# ----------------------------

def IsValidDate(DateText: str) -> bool:
    """Return True if DateText matches YYYY/MM/DD."""
    try:
        datetime.strptime(DateText, "%Y/%m/%d")
        return True
    except ValueError:
        return False


def PromptTransactionType() -> str:
    """Prompt until a valid transaction type is entered."""
    while True:
        Value = input("Expense or Income: ").strip().lower()
        if Value in {"expense", "income"}:
            return Value
        print("Please enter 'Expense' or 'Income'.")


def PromptCategory() -> str:
    """Prompt for a non-empty category (free-form for now)."""
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


def PromptAmount() -> float:
    """Prompt until a valid numeric amount is entered. Rounds to 2 decimals."""
    while True:
        Raw = input("Transaction Amount: ").strip()
        try:
            Amount = round(float(Raw), 2)
            return Amount
        except ValueError:
            print("Please enter a valid numeric value for amount.")


def PromptDate() -> str:
    """Prompt until a valid YYYY/MM/DD date is entered."""
    while True:
        Value = input("Transaction Date (YYYY/MM/DD): ").strip()
        if IsValidDate(Value):
            return Value
        print("Please enter a valid date in YYYY/MM/DD format.")


# ----------------------------
# Core CLI actions
# ----------------------------

def HandleTransaction() -> None:
    """
    Handle input of a transaction (expense or income) and persist it via the service.

    Side Effects:
        Prompts for input and prints status messages.

    Raises:
        Exceptions are caught and printed so the CLI remains responsive.
    """
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
        print(f"An unexpected error occurred while saving the transaction: {Ex}")


def HandleSummary() -> None:
    """
    Output the user's account summary in a simple table.

    Notes:
        Relies on GillPayService.GetTransactionSummary returning a dict with
        keys 'income', 'expense', and 'net'.
    """
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
        print(f"An unexpected error occurred while generating the summary: {Ex}")


def HandleReport(ReportType: str) -> None:
    """
    Display a report. Supported values: EXP_BY_CAT, SUMMARY_BY_MONTH.
    """
    try:
        GillPay = GillPayService()
        print()
        GillPay.GenerateReport(ReportType)
    except Exception as Ex:
        print(f"An unexpected error occurred while generating the report: {Ex}")


def _TryGetCategoryTotals(Service: GillPayService) -> Optional[Dict[str, float]]:
    """
    Best-effort attempt to obtain expense totals by category from the service.
    Returns None if unsupported.
    """
    try:
        return Service.GetExpenseTotalsByCategory()  # type: ignore[attr-defined]
    except AttributeError:
        return None
    except Exception:
        return None

def LaunchApp() -> None:
    """
    Launch the Tk GUI. Preferred: import and call gui.app:main().
    Fallback: run as a module so package imports work.
    """
    # Preferred path: call gui.app:main() directly if it exists
    try:
        from gui.app import main as GuiMain
        GuiMain()
        return
    except Exception as ex:
        # optional: print(f"[LaunchApp] module main() import failed: {ex}")
        pass

    # Fallback path: run as a module (NOT by file path)
    try:
        import sys, subprocess
        subprocess.run([sys.executable, "-m", "gui.app"], check=False)
    except Exception as ex:
        print(f"Could not launch GUI: {ex}")




def HandleMatplotlibChart() -> None:
    """
    Show a simple bar chart of Expense totals by Category using Matplotlib.
    Runs in the same process and blocks until the window is closed.
    """
    try:
        import matplotlib.pyplot as plt
    except Exception as Ex:
        print(f"Matplotlib is not available: {Ex}")
        return

    try:
        GillPay = GillPayService()
        TotalsByCategory = GillPay.GetExpenseTotalsByCategory()  # dict[str, float]
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

# ----------------------------
# CLI framing
# ----------------------------

    """
    Present a selection to the user:
    """

def PrintMenu() -> None:
    print("\nHowdy fellow money savers and welcome to the GillPay Finance Tracking Application!\n"
          "\nPlease make a selection from the menu below:\n")
    print("Press 1: Add Transaction")
    print("Press 2: Account Summary")
    print("Press 3: Expense by Category Report")
    print("Press 4: Spending By Month Report")
    print("Press 5: Fancy Chart")
    print("Press 6: Launch GUI")
    print("Press 7: Farewell!")


def main() -> None:
    """
    Interactive loop for GillPay.
    Will be replaced by GUI in later phases.
    """
    GillPayIsRunning = True
    try:
        while GillPayIsRunning:
            PrintMenu()
            try:
                UserChoice = int(input("Action: ").strip())
            except ValueError:
                print("You entered invalid data. Please enter a number between 1 and 6.")
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
                print("Invalid choice, please select value 1 - 6.")
    except KeyboardInterrupt:
        print("Session cancelled by user.")
    finally:
        GillPayLogo()
        print("Thank you for using GillPay for your finance tracking needs!")

# ----------------------------
# Fun: ASCII logo
# ----------------------------

def GillPayLogo():
    """
    Creates GillPay logo whenever user exits out of the application
    """
    print("             /`·.¸")
    print("            /¸...¸`:·")
    print("       ¸.·´  ¸   `·.¸.·´)")
    print("      : © ):´; GillPay¸  {")
    print("       `·.¸ `·  ¸.·´\\`·¸)")
    print("           `\\´´\\¸.·´")


if __name__ == "__main__":
    main()
