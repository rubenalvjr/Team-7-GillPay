# PROGRAM:     Main
# PURPOSE:     Launches GillPay application
# INPUT:       Ask for user input to create a transaction or view summary
# PROCESS:     Based on user input application call function to process users
# request
# OUTPUT:      Successful transaction creation or account summary
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

def HandleTransaction():
    """
    Module to handle input of a transaction (expense/income). A GUI will replace
    the data capturing in a later phase
    :return: None
    """
    # TODO - Add logic to handle this in GillPayService
    transactionType = input("Expense or Income: ")
    transactionCategory = input("Transaction Category: ")
    transactionAmount = input("Transaction Amount: ")
    transactionDate = input("Transaction Date (YYYY/MM/DD):")

    print()
    print(f"Your transaction is:")
    print(f"Type: {transactionType}")
    print(f"Type: {transactionCategory}")
    print(f"Type: ${transactionAmount}")
    print(f"Type: {transactionDate}")
    print(" " * 4)


def HandleSummary():
    """
    Module to handle the output of users account summary. A GUI will replace
    the data capturing in a later phase
    :return:
    """
    # TODO - Add logic to handle this in GillPayService
    totalIncome = 3000
    totalExpense = 200
    print()
    print(f"Your Total Income: {totalIncome}")
    print(f"Your Total Income: {totalExpense}")
    print(f"Your Total Income: {totalIncome - totalExpense}")
    print(" " * 4)


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
