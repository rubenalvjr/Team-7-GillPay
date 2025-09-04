# PROGRAM:     GillPayService
# PURPOSE:     Contains core business logic for GillPay application
# INPUT:       Takes in input/requests from GillPay GUI
# PROCESS:     Takes request data form GillPay GUI and processes it by
#                  performing data validation and interacting with data
#                  access layer
# OUTPUT:      Output is based on required data needed by user GUI interactions
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

class GillPayService:

    # TODO - Create logic to handle total income
    def GetTotalIncome(self):
        # Call TransactionDAO to get list of transactions
        # Filter out only Income transactions
        # Sum all the data
        # Return data
        return None

    # TODO - Create logic to handle total expenses
    def GetTotalExpenses(self):
        # Call TransactionDAO to get list of transactions
        # Filter out only Expense transactions
        # Sum all the data
        # Return data
        return None

    # TODO - Create logic to handle net income
    def GetNetIncome(self):
        # Call GetTotalIncome function to get total income
        # Call GetTotalExpenses function to get total income
        # Subtract total income data from total expense data
        # Return data
        return None

    # TODO - Create logic to adding a new Transaction
    def PostTransaction(self):
        return None
