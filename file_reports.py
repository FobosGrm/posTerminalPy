import os
from datetime import datetime

def save_txt_reports(shop_conn, bank_conn, log_conn):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shop_cur = shop_conn.cursor()
    bank_cur = bank_conn.cursor()
    log_cur = log_conn.cursor()

    # Save Inventory
    with open(os.path.join(base_dir, "shop.txt"), "w", encoding="utf-8") as f:
        f.write("--- INVENTORY ---\n")
        shop_cur.execute('SELECT * FROM products')
        for row in shop_cur.fetchall(): f.write(f"ID: {row[0]} | {row[1]} | {row[2]} UAH\n")

    # Save Customers
    with open(os.path.join(base_dir, "customers.txt"), "w", encoding="utf-8") as f:
        f.write("--- CUSTOMERS ---\n")
        shop_cur.execute('SELECT * FROM loyalty_cards')
        for row in shop_cur.fetchall(): f.write(f"Code: {row[0]} | {row[1]}\n")

    # Save Bank Accounts
    with open(os.path.join(base_dir, "bank.txt"), "w", encoding="utf-8") as f:
        f.write("--- BANK ---\n")
        bank_cur.execute('SELECT * FROM accounts')
        for row in bank_cur.fetchall(): f.write(f"Card: {row[0]} | Balance: {row[1]:.2f} UAH\n")

    # Log latest transaction
    log_file_path = os.path.join(base_dir, "logs.txt")
    log_cur.execute('SELECT * FROM transactions ORDER BY id DESC LIMIT 1')
    last_entry = log_cur.fetchone()

    if last_entry:
        with open(log_file_path, "a", encoding="utf-8") as f:
            line = f"Transaction #{last_entry[0]} | Customer: {last_entry[1]} | Total: {last_entry[3]} UAH | Time: {last_entry[4]}\nItems: {last_entry[2]}\n"
            f.write(line + "-"*30 + "\n")