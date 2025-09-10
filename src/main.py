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

    print(data)
    # print(f"Your Total Income: {totalIncome}")
    # print(f"Your Total Expenses: {totalExpense}")
    # print(f"Your Net Income: {totalIncome - totalExpense}")
    # print(" " * 4)


def main():
    """
    This logic is used to interact with data read and create functionality it
    will be replaced by GUI in later phases of the application development
    :return:
    """
    isGillPayRunning = True
    while isGillPayRunning:
        print("Howdy!! Fellow Money Savers!")
        print("Press 1 for adding a transaction")
        print("Press 2 for account summary")
        print("Press 3 to call it a day")
        try:
            userChoice = int(input("Action: "))
        except ValueError:
            print("You entered invalid data")

        if userChoice == 1:
            HandleTransaction()
        elif userChoice == 2:
            HandleSummary()
        else:
            isGillPayRunning = False

    print("Thank you for using GillPay for your finance needs!")


if __name__ == '__main__':
    main()
