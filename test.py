import unittest
import mysql.connector
from app import app

class FinancialServicesTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        self.db = mysql.connector.connect(
            host="financialservicesdb.cp4o40k6mxah.us-west-1.rds.amazonaws.com",
            user="admin",
            password="Sesat26535102020",
            database="financialServicesDB"
        )
        self.cursor = self.db.cursor()

    def tearDown(self):
        self.cursor.close()
        self.db.close()

    def test_transfer(self):
        # Initial state: check balances before transfer
        self.cursor.execute("SELECT Balance FROM Accounts WHERE AccountID = 102")
        from_balance_before = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT Balance FROM Accounts WHERE AccountID = 103")
        to_balance_before = self.cursor.fetchone()[0]

        # Perform the transfer
        response = self.app.post('/transfer', data={
            'Amount': 100,
            'FromAccountID': 102,
            'ToAccountID': 103
        })
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful transfer

        # Check balances after transfer
        self.cursor.execute("SELECT Balance FROM Accounts WHERE AccountID = 102")
        from_balance_after = self.cursor.fetchone()[0]
        self.cursor.execute("SELECT Balance FROM Accounts WHERE AccountID = 103")
        to_balance_after = self.cursor.fetchone()[0]

        # Check transaction records
        self.cursor.execute("SELECT * FROM Transactions WHERE AccountID IN (102, 103)")
        transactions = self.cursor.fetchall()

        self.assertEqual(from_balance_after, from_balance_before - 100)
        self.assertEqual(to_balance_after, to_balance_before + 100)
        self.assertEqual(len(transactions), 2)  # Ensure two transactions are recorded

if __name__ == '__main__':
    unittest.main()
