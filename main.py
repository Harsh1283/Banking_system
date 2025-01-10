import mysql.connector
from hashlib import sha256
import random
import re

# Function to connect to MySQL Database
def connect_db():
    return mysql.connector.connect(
        host="localhost",      # Host where MySQL is running
        user="root",           # Your MySQL username (adjust accordingly)
        password="harsh",  # Your MySQL password
        database="banking_system" # Database name
    )

# Function to validate password (must meet requirements)
def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):  # Must have lowercase
        return False
    if not re.search("[A-Z]", password):  # Must have uppercase
        return False
    if not re.search("[0-9]", password):  # Must have a digit
        return False
    return True

# Function to add a new user (register user)
def add_user(name, dob, city, password, balance, contact_number, email, address):
    # Generate a random 10-digit account number
    account_number = str(random.randint(1000000000, 9999999999))

    # Hash the password
    hashed_password = sha256(password.encode()).hexdigest()

    # Connect to the database
    conn = connect_db()
    cursor = conn.cursor()

    # Insert user details into the 'users' table
    cursor.execute('''INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (name, account_number, dob, city, hashed_password, balance, contact_number, email, address))

    # Insert login credentials into the 'login' table
    cursor.execute('''INSERT INTO login (account_number, password) VALUES (%s, %s)''', 
                   (account_number, hashed_password))

    conn.commit()
    conn.close()

    return account_number  # Return the generated account number


def record_transaction(account_number, transaction_type, amount):
    """
    Records a transaction in the transactions table.
    
    :param account_number: Account number for the transaction
    :param transaction_type: Type of transaction ('credit', 'debit', 'transfer')
    :param amount: Amount of the transaction
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (account_number, transaction_type, amount)
            VALUES (%s, %s, %s)
        ''', (account_number, transaction_type, amount))
        conn.commit()
        print("Transaction recorded successfully.")
    except Exception as e:
        print("Error recording transaction:", e)
    finally:
        conn.close()




# Function to display post-login menu and handle user actions
def post_login_menu(account_number):
    while True:
        print("\nWelcome to your account!")
        print("1. Show Balance")
        print("2. Show Transactions")
        print("3. Credit Amount")
        print("4. Debit Amount")
        print("5. Transfer Amount")
        print("6. Activate/Deactivate Account")
        print("7. Change Password")
        print("8. Update Profile")
        print("9. Logout")

        choice = input("Choose an option: ")

        if choice == '1':
            # Show Balance
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE account_number = %s", (account_number,))
            balance = cursor.fetchone()
            if balance:
                print(f"Your current balance is: ₹{balance[0]}")
            else:
                print("Unable to fetch balance.")
            conn.close()

        elif choice == '2':
            # Show Transactions
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM transactions WHERE account_number = %s", (account_number,))
            transactions = cursor.fetchall()
            if transactions:
                print("Transaction History:")
                for txn in transactions:
                    print(f"ID: {txn[0]}, Type: {txn[2]}, Amount: ₹{txn[3]}, Date: {txn[4]}")
            else:
                print("No transactions found.")
            conn.close()

        elif choice == '3':
            # Credit Amount
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT active FROM users WHERE account_number = %s", (account_number,))
            is_active = cursor.fetchone()
            if is_active and is_active[0]:
                amount = float(input("Enter the amount to credit: "))
                cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
                conn.commit()
                record_transaction(account_number, 'credit', amount)
                print(f"₹{amount} credited to your account.")
            else:
                print("Your account is deactivated. Activate it to perform transactions.")
            conn.close()

        elif choice == '4':
            # Debit Amount
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT active, balance FROM users WHERE account_number = %s", (account_number,))
            result = cursor.fetchone()
            if result and result[0]:
                balance = result[1]
                amount = float(input("Enter the amount to debit: "))
                if balance >= amount:
                    cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
                    conn.commit()
                    record_transaction(account_number, 'debit', amount)
                    print(f"₹{amount} debited from your account.")
                else:
                    print("Insufficient balance.")
            else:
                print("Your account is deactivated. Activate it to perform transactions.")
            conn.close()

        elif choice == '5':
            # Transfer Amount
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT active, balance FROM users WHERE account_number = %s", (account_number,))
            result = cursor.fetchone()
            if result and result[0]:
                balance = result[1]
                target_account = input("Enter the target account number: ")
                amount = float(input("Enter the amount to transfer: "))
                if balance >= amount:
                    cursor.execute("SELECT active FROM users WHERE account_number = %s", (target_account,))
                    target_active = cursor.fetchone()
                    if target_active and target_active[0]:
                        # Deduct from sender
                        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
                        # Add to recipient
                        cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, target_account))
                        conn.commit()
                        record_transaction(account_number, 'transfer_out', amount)
                        record_transaction(target_account, 'transfer_in', amount)
                        print(f"₹{amount} transferred to account {target_account}.")
                    else:
                        print("Target account is deactivated or does not exist.")
                else:
                    print("Insufficient balance.")
            else:
                print("Your account is deactivated. Activate it to perform transactions.")
            conn.close()

        elif choice == '6':
            # Activate/Deactivate Account
            status = input("Do you want to activate or deactivate your account? (activate/deactivate): ").lower()
            conn = connect_db()
            cursor = conn.cursor()
            is_active = 1 if status == "activate" else 0
            cursor.execute("UPDATE users SET active = %s WHERE account_number = %s", (is_active, account_number))
            conn.commit()
            print(f"Your account has been {'activated' if is_active else 'deactivated'}.")
            conn.close()

        elif choice == '7':
            # Change Password
            new_password = input("Enter your new password: ")
            while not validate_password(new_password):
                print("Password doesn't meet criteria. Try again.")
                new_password = input("Enter your new password: ")
            hashed_password = sha256(new_password.encode()).hexdigest()
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("UPDATE login SET password = %s WHERE account_number = %s", (hashed_password, account_number))
            conn.commit()
            print("Password updated successfully.")
            conn.close()

        elif choice == '8':
            # Update Profile
            name = input("Enter new name: ")
            dob = input("Enter new date of birth (YYYY-MM-DD): ")
            city = input("Enter new city: ")
            contact_number = input("Enter new contact number: ")
            email = input("Enter new email: ")
            address = input("Enter new address: ")

            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET name = %s, dob = %s, city = %s, contact_number = %s, email = %s, address = %s 
                WHERE account_number = %s
            ''', (name, dob, city, contact_number, email, address, account_number))
            conn.commit()
            print("Profile updated successfully.")
            conn.close()

        elif choice == '9':
            # Logout
            print("You have been logged out.")
            break

        else:
            print("Invalid choice. Please try again.")





# Function to handle user login
# Function to handle user login
def login_user(account_number, password):
    # Hash the password entered by the user
    hashed_password = sha256(password.encode()).hexdigest()

    # Connect to the database
    conn = connect_db()
    cursor = conn.cursor()

    # Verify the account number and password from the 'login' table
    cursor.execute('''SELECT * FROM login WHERE account_number = %s AND password = %s''', 
                   (account_number, hashed_password))
    user = cursor.fetchone()

    conn.close()

    if user:
        print("Login successful.")
        post_login_menu(account_number)  # Call the post-login menu
        return True
    else:
        print("Invalid account number or password.")
        return False



# Main program for registering or logging in
def main():
    while True:
        print("\nBanking System")
        print("1. Add User (Register)")
        print("2. Login")
        print("3. Exit")
        
        choice = input("Choose an option: ")

        if choice == '1':
            # Register a new user
            name = input("Enter name: ")
            dob = input("Enter date of birth (YYYY-MM-DD): ")
            city = input("Enter city: ")
            contact_number = input("Enter contact number: ")
            email = input("Enter email: ")
            address = input("Enter address: ")

            password = input("Enter password (8+ characters, with uppercase, lowercase, and digits): ")
            while not validate_password(password):
                print("Password doesn't meet criteria. Try again.")
                password = input("Enter password (8+ characters, with uppercase, lowercase, and digits): ")

            balance = float(input("Enter initial balance (minimum 2000): "))
            while balance < 2000:
                print("Initial balance must be at least 2000.")
                balance = float(input("Enter initial balance (minimum 2000): "))

            account_number = add_user(name, dob, city, password, balance, contact_number, email, address)
            print(f"User registered successfully! Account Number: {account_number}")

        elif choice == '2':
            # Login
            account_number = input("Enter account number: ")
            password = input("Enter password: ")
            login_user(account_number, password)

        elif choice == '3':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
