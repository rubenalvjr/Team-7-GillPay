# PROGRAM:     Transaction
# AUTHOR:      Team 7
# PURPOSE:     Core Data Model used for GillPay processes
# INPUT:       Transaction values (Type, Category, Amount, Date)
# PROCESS:     Acts as container of data representing a row of
#                      data (Transaction)
# OUTPUT:      Transaction Object
# HONOR CODE:  On my honor, as an Aggie, I have neither given nor
#               received unauthorized aid on this academic work.

class Transaction:

    def __init__(self, transaction: str, category: str, amount: float,
                 date: str):
        """
        Constructor with required parameters needed to initial object
        """
        self.transaction_type = transaction
        self.category = category
        self.amount = amount
        self.date = date
