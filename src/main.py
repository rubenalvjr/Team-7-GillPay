# PROGRAM:     Main
# AUTHOR:      Team 7
# PURPOSE:     Launches GillPay application
# INPUT:       Ask for user input to create a transaction or view summary
# PROCESS:     - User selects 1 then inputs data to capture transaction
#              - User selects 2 then account summary info is displayed
#              - User selects 3 then exits application loop
# OUTPUT:      Successful transaction creation or account summary
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#              received unauthorized aid on this academic work.

from src.gillpay_service import GillPayService
from src.models.transaction import Transaction


def HandleTransaction():
    """
    Handle input of a transaction (expense/income).
    A GUI will replace this CLI data capture in a later phase.
    """
    try:
        gillpay = GillPayService()

        print()
        # Collect transaction details from user
        transactionType = input("Expense or Income: ").lower()
        transactionCategory = input("Transaction Category: ").lower()
        transactionDescription = input("Transaction Description: ")
        transactionAmount = round(float(input("Transaction Amount: ")), 2)
        transactionDate = input("Transaction Date (YYYY/MM/DD): ")

        # Create Transaction object with all 5 fields
        transaction = Transaction(
            transaction=transactionType,
            category=transactionCategory,
            description=transactionDescription,
            amount=transactionAmount,
            date=transactionDate
        )

        gillpay.PostTransaction(transaction)
    except ValueError:
        print("Please enter a valid numeric value for amount!")


def HandleSummary():
    """
    Output the user's account summary.
    A GUI will replace this CLI display in a later phase.
    """
    gillpay = GillPayService()
    summaryData = gillpay.GetTransactionSummary()
    print()
    print(f"{'-' * 5} Account Summary {'-' * 5}")
    print(f"{'Description':10} {'Amount':>10}")
    print(f"{'Income':10} {summaryData['income']:>10.2f}")
    print(f"{'Expense':10} {summaryData['expense']:>10.2f}")
    print(f"{'Net':10} {summaryData['net']:>10.2f}")


def main():
    """
    Interactive loop for GillPay.
    Will be replaced by GUI in later phases.
    """
    gillPayIsRunning = True
    while gillPayIsRunning:
        print()
        print("Howdy!! Fellow Money Savers!")
        print()
        print("Press 1: Add Transaction")
        print("Press 2: Account Summary")
        print("Press 3: Farewell!")

        try:
            userChoice = int(input("Action: "))
        except ValueError:
            print("You entered invalid data")
            continue

        if userChoice == 1:
            HandleTransaction()
        elif userChoice == 2:
            HandleSummary()
        elif userChoice == 3:
            gillPayIsRunning = False
        else:
            print("Invalid choice, please select 1, 2, or 3.")

    print("Thank you for using GillPay for your finance tracking needs!")


if __name__ == '__main__':
    main()
