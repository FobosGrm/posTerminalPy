import sqlite3
import os

def setup_databases():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_paths = {
        'shop': os.path.join(base_dir, 'shop_server.db'),
        'bank': os.path.join(base_dir, 'bank_server.db'),
        'logs': os.path.join(base_dir, 'logs_server.db')
    }

    # SHOP DB
    shop_conn = sqlite3.connect(db_paths['shop'])
    shop_cur = shop_conn.cursor()
    shop_cur.execute('CREATE TABLE IF NOT EXISTS products (id TEXT PRIMARY KEY, name TEXT, price REAL)')
    shop_cur.execute('CREATE TABLE IF NOT EXISTS loyalty_cards (card_id TEXT PRIMARY KEY, owner TEXT)')
    
    products = [
        ('1','Bread',25.5), ('2','Milk',42.0), ('3','Coffee',150.0), 
        ('4','Apples',35.0), ('5','Chocolate',65.0), ('6','Cheese',95.0), 
        ('7','Tea',55.0), ('8','Juice',48.0), ('9','Cookies',38.0)
    ]
    shop_cur.executemany('INSERT OR REPLACE INTO products VALUES (?,?,?)', products)
    
    customers = [
        ('777','Anton Kryvoshey'), 
        ('666','Rostyslav Zamula'), 
        ('555','Artem Prokopenko'), 
        ('000','Staff')
    ]
    shop_cur.executemany('INSERT OR REPLACE INTO loyalty_cards VALUES (?,?)', customers)
    shop_conn.commit()

    # BANK DB
    bank_conn = sqlite3.connect(db_paths['bank'])
    bank_cur = bank_conn.cursor()
    bank_cur.execute('CREATE TABLE IF NOT EXISTS accounts (card_number TEXT PRIMARY KEY, balance REAL)')
    
    accounts = [
        ('4441111100007777', 1000.0), ('5375111100006666', 1000.0), 
        ('4441111100005555', 1000.0), ('4444111100000000', 5000.0)
    ]
    bank_cur.executemany('INSERT OR IGNORE INTO accounts VALUES (?,?)', accounts)
    bank_conn.commit()

    # LOGS DB
    log_conn = sqlite3.connect(db_paths['logs'])
    log_cur = log_conn.cursor()
    log_cur.execute('CREATE TABLE IF NOT EXISTS transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, items TEXT, total REAL, timestamp TEXT)')
    log_conn.commit()
    
    return shop_conn, bank_conn, log_conn