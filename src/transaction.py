class Transaction:

    def __init__(self, transaction: str, category: str, amount: int, date: str):
        self.transaction_type = transaction
        self.category = category
        self.amount = amount
        self.date = date