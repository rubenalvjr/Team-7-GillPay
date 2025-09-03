from src.transaction_dao import TransactionDAO
from src.transaction import Transaction

transaction_dao = TransactionDAO()
#transaction = Transaction("Expense","Entertainment", 20, "2025/08/15")

#transaction_dao.save_transaction(transaction)
print(transaction_dao.get_all_transactions())
