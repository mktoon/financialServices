from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Create a connection to the database
def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="financialservicesdb"
    )

# Route to display all customers
@app.route('/')
def index():
    # Total customers
    total_customers = Customer.query.count()

    # Total accounts
    total_accounts = Account.query.count()

    # Transactions today
    today = date.today()
    transactions_today = Transaction.query.filter(Transaction.date == today).count()

    # Pending notifications
    pending_notifications = Notification.query.filter_by(status='pending').count()

    # Recent Activity (example: 5 most recent transactions)
    recent_transactions = Transaction.query.order_by(Transaction.date.desc()).limit(5).all()

    return render_template('index.html',
                           total_customers=total_customers,
                           total_accounts=total_accounts,
                           transactions_today=transactions_today,
                           pending_notifications=pending_notifications,
                           recent_transactions=recent_transactions)

# Route to display form for creating a new customer
@app.route('/create', methods=['GET', 'POST'])
def create_customer():
    if request.method == 'POST':
        data = request.form
        db = create_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Customers (CustomerID, Name, Email, PhoneNumber, Address, DateOfBirth) VALUES (%s, %s, %s, %s, %s, %s)",
            (data['CustomerID'], data['Name'], data['Email'], data['PhoneNumber'], data['Address'], data['DateOfBirth'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))
    return render_template('create.html')

# Route to display form for updating a customer
@app.route('/update/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            "UPDATE Customers SET Name = %s, Email = %s, PhoneNumber = %s, Address = %s, DateOfBirth = %s WHERE CustomerID = %s",
            (data['Name'], data['Email'], data['PhoneNumber'], data['Address'], data['DateOfBirth'], customer_id)
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))
    
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = %s", (customer_id,))
    customer = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('update.html', customer=customer)

# Route to confirm and delete a customer
@app.route('/delete/<int:customer_id>', methods=['GET', 'POST'])
def delete_customer_page(customer_id):
    if request.method == 'POST':
        db = create_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM Customers WHERE CustomerID = %s", (customer_id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('index'))
    return render_template('delete.html', customer_id=customer_id)


# Route to view all customers
@app.route('/view_customers', methods=['GET'])
def view_customers():
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('view_customers.html', customers=customers)


# Route to display form for creating a new account
@app.route('/createAccount', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        data = request.form
        db = create_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Accounts (AccountID, CustomerID, AccountType, Balance, DateOpened) VALUES (%s, %s, %s, %s, %s)",
            (data['AccountID'], data['CustomerID'], data['AccountType'], data['Balance'], data['DateOpened'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('view_accounts'))
    return render_template('create_account.html')


# Retrieve all accounts for a customer
@app.route('/accounts/<int:customer_id>', methods=['GET'])
def get_accounts(customer_id):
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE CustomerID = %s", (customer_id,))
    accounts = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(accounts)

# Retrieve a single account by AccountID
@app.route('/account/<int:account_id>', methods=['GET'])
def get_account(account_id):
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE AccountID = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    db.close()
    return jsonify(account)

# Update an account
# Route to display form for updating an account
@app.route('/updateAccount/<int:account_id>', methods=['GET', 'POST'])
def update_account(account_id):
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        data = request.form
        cursor.execute(
            "UPDATE Accounts SET AccountType = %s, Balance = %s WHERE AccountID = %s",
            (data['AccountType'], data['Balance'], account_id)
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('view_accounts'))
    
    cursor.execute("SELECT * FROM Accounts WHERE AccountID = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('update_account.html', account=account)

# Route to confirm and delete an account
@app.route('/deleteAccount/<int:account_id>', methods=['GET', 'POST'])
def delete_account(account_id):
    if request.method == 'POST':
        db = create_connection()
        cursor = db.cursor()
        cursor.execute("DELETE FROM Accounts WHERE AccountID = %s", (account_id,))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('view_accounts'))
    
    # Fetch account details to display in the confirmation page
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts WHERE AccountID = %s", (account_id,))
    account = cursor.fetchone()
    cursor.close()
    db.close()

    if not account:
        return "Account not found", 404  # Handle the case where the account is not found

    return render_template('delete_account.html', account=account)


# Route to view all accounts (you can call this 'view_accounts')
@app.route('/accounts', methods=['GET'])
def view_accounts():
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Accounts")
    accounts = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('accounts.html', accounts=accounts)

# dashboard route that displays total number of customers, accounts, total balance, and recent transactions
@app.route('/dashboard')
def dashboard():
    db = create_connection()
    cursor = db.cursor(dictionary=True)

    # Get total number of customers
    cursor.execute("SELECT COUNT(*) as total_customers FROM Customers")
    total_customers = cursor.fetchone()['total_customers']

    # Get total number of accounts
    cursor.execute("SELECT COUNT(*) as total_accounts FROM Accounts")
    total_accounts = cursor.fetchone()['total_accounts']

    # Get total balance across all accounts
    cursor.execute("SELECT SUM(Balance) as total_balance FROM Accounts")
    total_balance = cursor.fetchone()['total_balance']

    # Get recent transactions (e.g., last 5 transactions)
    cursor.execute("SELECT * FROM Transactions ORDER BY TransactionDate DESC LIMIT 5")
    recent_transactions = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('dashboard.html', 
                           total_customers=total_customers, 
                           total_accounts=total_accounts, 
                           total_balance=total_balance, 
                           recent_transactions=recent_transactions)

#  this route is responsible for displaying transactions(withdrawal and deposits, transfers)
@app.route('/transactions', methods=['GET'])
def view_transactions():
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Transactions")
    transactions = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('transactions.html', transactions=transactions)


# Route to display form for creating a new transaction
@app.route('/create_transaction', methods=['GET', 'POST'])
def create_transaction():
    if request.method == 'POST':
        data = request.form
        transaction_id = data['TransactionID']
        account_id = data['AccountID']
        transaction_type = data['TransactionType']
        amount = float(data['Amount'])
        transaction_date = data['TransactionDate']
        status = data['Status']
        
        # Create a new transaction
        db = create_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Transactions (TransactionID, AccountID, TransactionType, Amount, TransactionDate, Status) VALUES (%s, %s, %s, %s, %s, %s)",
            (transaction_id, account_id, transaction_type, amount, transaction_date, status)
        )
        
        # Update the balance based on the transaction type
        if transaction_type == 'Deposit':
            cursor.execute("UPDATE Accounts SET Balance = Balance + %s WHERE AccountID = %s", (amount, account_id))
        elif transaction_type == 'Withdrawal':
            cursor.execute("UPDATE Accounts SET Balance = Balance - %s WHERE AccountID = %s", (amount, account_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return redirect(url_for('view_transactions'))
    
    return render_template('create_transaction.html')

# route to update a balance after a transaction has been done
@app.route('/update_balance/<int:account_id>', methods=['POST'])
def update_balance(account_id):
    data = request.form
    new_balance = float(data['Balance'])
    
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("UPDATE Accounts SET Balance = %s WHERE AccountID = %s", (new_balance, account_id))
    db.commit()
    cursor.close()
    db.close()
    
    return redirect(url_for('view_accounts'))


# route to update a transaction
@app.route('/transaction/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    data = request.json
    db = create_connection()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE Transactions SET AccountID = %s, TransactionType = %s, Amount = %s, TransactionDate = %s, Status = %s WHERE TransactionID = %s",
            (data['AccountID'], data['TransactionType'], data['Amount'], data['TransactionDate'], data['Status'], transaction_id)
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        db.close()

    return jsonify({'message': 'Transaction updated successfully'})

# route to delete a transaction
@app.route('/transaction/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    db = create_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Transactions WHERE TransactionID = %s", (transaction_id,))
    db.commit()
    cursor.close()
    db.close()
    return jsonify({'message': 'Transaction deleted successfully'})

# Route to search/filter transactions
@app.route('/search_transactions', methods=['GET'])
def search_transactions():
    criteria = request.args.get('criteria', '')
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    
    # Example search by transaction type, you can adjust this to search by other fields as needed
    cursor.execute("SELECT * FROM Transactions WHERE TransactionType LIKE %s", (f'%{criteria}%',))
    transactions = cursor.fetchall()
    
    cursor.close()
    db.close()
    return render_template('view_transactions.html', transactions=transactions)

# route for a payment processing
@app.route('/create_payment', methods=['GET', 'POST'])
def create_payment():
    if request.method == 'POST':
        data = request.form
        db = create_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Payments (PaymentID, TransactionID, PaymentDate, Amount, PaymentStatus) VALUES (%s, %s, %s, %s, %s)",
            (data['PaymentID'], data['TransactionID'], data['PaymentDate'], data['Amount'], data['PaymentStatus'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('view_payments'))
    return render_template('create_payment.html')

# route to view payments
@app.route('/payments', methods=['GET'])
def view_payments():
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Payments")
    payments = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('payments.html', payments=payments)

#route to view notification
@app.route('/notifications', methods=['GET'])
def view_notifications():
    db = create_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Notifications")
    notifications = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('notifications.html', notifications=notifications)

# route to create a notification
@app.route('/create_notification', methods=['GET', 'POST'])
def create_notification():
    if request.method == 'POST':
        data = request.form
        db = create_connection()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Notifications (NotificationID, AccountID, Message, Status) VALUES (%s, %s, %s, %s)",
            (data['NotificationID'], data['AccountID'], data['Message'], data['Status'])
        )
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('view_notifications'))
    return render_template('create_notification.html')

# this route is responsible for bank transfers(deposit, withdrawal, )
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        amount = float(request.form['Amount'])
        from_account_id = int(request.form['FromAccountID'])
        to_account_id = int(request.form['ToAccountID'])

        db =  create_connection()
        cursor = db.cursor()

        cursor.execute("START TRANSACTION")
        try:
            # Withdraw from the source account
            cursor.execute("UPDATE Accounts SET Balance = Balance - %s WHERE AccountID = %s", (amount, from_account_id))
            # Deposit into the destination account
            cursor.execute("UPDATE Accounts SET Balance = Balance + %s WHERE AccountID = %s", (amount, to_account_id))
            # Insert transfer transaction records
            cursor.execute(
                "INSERT INTO Transactions (TransactionID, AccountID, TransactionType, Amount, TransactionDate, Status) VALUES (UUID(), %s, 'Transfer Out', %s, NOW(), 'Completed')",
                (from_account_id, amount)
            )
            cursor.execute(
                "INSERT INTO Transactions (TransactionID, AccountID, TransactionType, Amount, TransactionDate, Status) VALUES (UUID(), %s, 'Transfer In', %s, NOW(), 'Completed')",
                (to_account_id, amount)
            )
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Transaction failed: {e}")
        finally:
            cursor.close()
            db.close()
        
        return redirect(url_for('view_transactions'))

    return render_template('create_transfer.html')


if __name__ == '__main__':
    app.run(debug=True)
