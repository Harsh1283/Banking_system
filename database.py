# database.py
import mysql.connector

def get_connection(database=None):
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="harsh",  # Replace with your MySQL password
        database=database
    )

def setup_database():
    # Initial connection without specifying the database
    conn = get_connection()
    cursor = conn.cursor()

    # Create the database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS banking_system")
    conn.close()

    # Reconnect to the newly created database
    conn = get_connection(database="banking_system")
    cursor = conn.cursor()

    # Create Tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        account_number VARCHAR(10) PRIMARY KEY,
        name VARCHAR(255),
        dob DATE,
        city VARCHAR(100),
        password VARCHAR(255),
        balance DOUBLE,
        contact_number VARCHAR(10),
        email VARCHAR(255),
        address TEXT,
        active BOOLEAN DEFAULT TRUE
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INT AUTO_INCREMENT PRIMARY KEY,
        account_number VARCHAR(10),
        transaction_type VARCHAR(50),
        amount DOUBLE,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(account_number) REFERENCES users(account_number)
    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()
    print("Database setup completed.")
