# PROGRAM:     Main
# AUTHOR:      Team 7
# PURPOSE:     Launches GillPay application
# INPUT:       Ask for user input to create a transaction or view summary
# PROCESS:     - User selects 1 than inputs render to capture transaction
#              - User selects 2 than account summary info is displayed
#              - User selects 3 than application break from loop
# OUTPUT:      Successful transaction creation or account summary
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.
from src.gillpay_service import GillPayService
from src.transaction import Transaction


def HandleTransaction():
    """
    Module to handle input of a transaction (expense/income). A GUI will replace
    the data capturing in a later phase
    """
    gillpay = GillPayService()

    print()
    # Engages user to input transaction data
    transactionType = input("Expense or Income: ").lower()
    transactionCategory = input("Transaction Category: ").lower()
    transactionAmount = round(float(input("Transaction Amount: ")), 2)
    transactionDate = input("Transaction Date (YYYY/MM/DD): ")
    transaction = Transaction(transactionType, transactionCategory,
                              transactionAmount, transactionDate)
    gillpay.PostTransaction(transaction)


def HandleSummary():
    """
    Module to handle the output of users account summary. A GUI will replace
    the data capturing in a later phase
    """
    gillpay = GillPayService()
    summaryData = gillpay.GetTransactionSummary()
    print()
    print(f"{'-' * 5} Account Summary {'-' * 5}")
    print(f"{'Description':10} {'Amount':>10}")
    print(f"{'Income':10} {summaryData["income"]:>10.2f}")
    print(f"{'Expense':10} {summaryData["expense"]:>10.2f}")
    print(f"{'Net':10} {summaryData["net"]:>10.2f}")


def main():
    """
    This logic is used to interact with data read and create functionality it
    will be replaced by GUI in later phases of the application development
    :return:
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

        if userChoice == 1:
            HandleTransaction()
        elif userChoice == 2:
            HandleSummary()
        else:
            gillPayIsRunning = False

    print("Thank you for using GillPay for your finance tracking needs!")


if __name__ == '__main__':
    main()
