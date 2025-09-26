# PROGRAM:     Main
# AUTHOR:      Team 7
# PURPOSE:     Launches GillPay application
# INPUT:       Ask for user input to create a transaction or view summary
# PROCESS:     - User selects 1 then inputs data to capture transaction
#              - User selects 2 then account summary info is displayed
#              - User selects 3 then Expense by Category Report is displayed
#              - User selects 4 then Spending By Month Report is displayed
#              - User selects 5 then application is closed
# OUTPUT:      Successful transaction creation or account summary
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#              received unauthorized aid on this academic work.
from selectors import SelectSelector

from src.gillpay_service import GillPayService
from src.models.transaction import Transaction


def HandleTransaction():
    """
    Handle input of a transaction (expense/income).
    A GUI will replace this CLI data capture in a later phase.
    """
    try:
        # Instantiate GillPayService object
        gillpay = GillPayService()

        print()
        # Collect transaction details from user
        transactionType = input("Expense or Income: ").lower()
        HandleTransactionValidation(transactionType)
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

        # Post Transaction to CSV
        gillpay.PostTransaction(transaction)
    except ValueError:
        # Notification to user that non-numeric values was entered
        print("Please enter a valid numeric value for amount!")
    except TypeError:
        # Notification to user that invalid Transaction type was entered
        print("You entered value other than Income or Expense")


def HandleTransactionValidation(transactionType):
    """
    Validates user input is either Income or Expense
    """
    if transactionType != "expense" or transactionType != "income":
        raise TypeError


def HandleSummary():
    """
    Output the user's Account Summary.
    A GUI will replace this CLI display in a later phase.
    """
    gillpay = GillPayService()
    gillpay.GetTransactionSummary()


def HandleReport(reportType):
    """
    Displays the report for all expenses by category from highest
    to lowest total
    """
    gillpay = GillPayService()
    gillpay.GenerateReport(reportType)

def GillPayLogo():
    """
    Creates GillPay logo whenever user exits out of the application
    """
    print("             /`·.¸")
    print("            /¸...¸`:·")
    print("       ¸.·´  ¸   `·.¸.·´)")
    print("      : © ):´;      ¸  {")
    print("       `·.¸ `·  ¸.·´\\`·¸)")
    print("           `\\´´\\¸.·´")


def main():
    """
    Interactive loop for GillPay.
    Will be replaced by GUI in later phases.
    """
    gillPayIsRunning = True

    # Keeps application running until user exits out of application (5)
    while gillPayIsRunning:
        print()
        print("Please make a choice:")
        print("1: Add Transaction")
        print("2: Account Summary")
        print("3: Expense by Category Report")
        print("4: Spending By Month Report")
        print("5: Farewell!")

        try:
            userChoice = int(input("Action: "))
        except ValueError:
            print()
            # Handles error if user enters a non-numeric value
            print(f"You entered invalid data!")
            print("Please enter value 1 - 5")
            continue

        if userChoice == 1:
            HandleTransaction()
        elif userChoice == 2:
            HandleSummary()
        elif userChoice == 3:
            HandleReport("EXP_BY_CAT")
        elif userChoice == 4:
            HandleReport("SUMMARY_BY_MONTH")
        elif userChoice == 5:
            gillPayIsRunning = False
        else:
            # Informs user that invalid numeric value was entered
            print("Invalid choice, please select value 1 - 5.")

    print("Thank you for using GillPay for your finance tracking needs!")
    GillPayLogo()


if __name__ == '__main__':
    main()
