import sqlite3
import os
from datetime import datetime

def setup_databases():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    db_paths = {
        'shop': os.path.join(base_dir, 'shop_server.db'),
        'bank': os.path.join(base_dir, 'bank_server.db'),
        'logs': os.path.join(base_dir, 'logs_server.db')
    }

    for path in db_paths.values():
        if os.path.exists(path): os.remove(path)

    # МАГАЗИН---------------------------------------------------------------------
    shop_conn = sqlite3.connect(db_paths['shop'])
    shop_cur = shop_conn.cursor()
    shop_cur.execute('CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT, price REAL)')
    shop_cur.execute('CREATE TABLE loyalty_cards (card_id TEXT PRIMARY KEY, owner TEXT)')
    products = [('1','Хліб',25.5), ('2','Молоко',42.0), ('3','Кава',150.0), ('4','Яблука',35.0), 
                ('5','Шоколад',65.0), ('6','Сир',95.0), ('7','Чай',55.0), ('8','Сік',48.0), ('9','Печиво',38.0)]
    shop_cur.executemany('INSERT INTO products VALUES (?,?,?)', products)
    
    customers = [('777','Антон Кривошей'), ('666','Ростислав Замула'), ('555','Артем Прокопенко'), ('000','Персонал')]
    shop_cur.executemany('INSERT INTO loyalty_cards VALUES (?,?)', customers)
    shop_conn.commit()

    # БАНК КАРТИ----------------------------------------------------------------------------------
    bank_conn = sqlite3.connect(db_paths['bank'])
    bank_cur = bank_conn.cursor()
    bank_cur.execute('CREATE TABLE accounts (card_number TEXT PRIMARY KEY, balance REAL)')
    accounts = [('4441111100007777', 1000.0), ('5375111100006666', 1000.0), 
                ('4441111100005555', 1000.0), ('4444111100000000', 5000.0)]
    bank_cur.executemany('INSERT INTO accounts VALUES (?,?)', accounts)
    bank_conn.commit()

    # ЛОГИ(SQL)------------------------------------------------------------------------
    log_conn = sqlite3.connect(db_paths['logs'])
    log_cur = log_conn.cursor()
    log_cur.execute('CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT, customer TEXT, items TEXT, total REAL, timestamp TEXT)')
    log_conn.commit()
    
    return shop_conn, bank_conn, log_conn

def save_txt_reports(shop_conn, bank_conn):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shop_cur = shop_conn.cursor()
    bank_cur = bank_conn.cursor()

    with open(os.path.join(base_dir, "shop.txt"), "w", encoding="utf-8") as f:
        f.write("--- АСОРТИМЕНТ ---\n")
        shop_cur.execute('SELECT * FROM products')
        for row in shop_cur.fetchall(): f.write(f"ID: {row[0]} | {row[1]} | {row[2]} грн\n")

    with open(os.path.join(base_dir, "customers.txt"), "w", encoding="utf-8") as f:
        f.write("--- КЛІЄНТИ ---\n")
        shop_cur.execute('SELECT * FROM loyalty_cards')
        for row in shop_cur.fetchall(): f.write(f"Код: {row[0]} | {row[1]}\n")

    with open(os.path.join(base_dir, "bank.txt"), "w", encoding="utf-8") as f:
        f.write("--- БАНК ---\n")
        bank_cur.execute('SELECT * FROM accounts')
        for row in bank_cur.fetchall(): f.write(f"Карта: {row[0]} | Баланс: {row[1]:.2f} грн\n")

def run_self_checkout():
    shop_conn, bank_conn, log_conn = setup_databases()
    shop_cur, bank_cur, log_cur = shop_conn.cursor(), bank_conn.cursor(), log_conn.cursor()

    print("\n" + "="*50 + "\n--- КАСА САМООБСЛУГОВУВАННЯ ---\n" + "="*50)

    card_loyalty = input("Відскануйте карту покупця (код): ").strip()
    shop_cur.execute('SELECT owner FROM loyalty_cards WHERE card_id = ?', (card_loyalty,))
    user_res = shop_cur.fetchone()
    user_name = user_res[0] if user_res else "Гість"
    print(f"Вітаємо: {user_name}!")

    cart_items, cart_total = [], 0

    while True:
        print(f"\n[ КОШИК: {len(cart_items)} тов. | СУМА: {cart_total:.2f} грн ]")
        cmd = input("ID товару(ів), '?' - меню, 'y' - ОПЛАТА: ").strip().lower()

        if cmd == 'y':
            if not cart_items: continue
            print(f"\nДо сплати: {cart_total:.2f} грн")
            bank_card = input("Вставте банківську карту: ").strip()
            bank_cur.execute('SELECT balance FROM accounts WHERE card_number = ?', (bank_card,))
            acc = bank_cur.fetchone()

            if acc and acc[0] >= cart_total:
                new_bal = acc[0] - cart_total
                bank_cur.execute('UPDATE accounts SET balance = ? WHERE card_number = ?', (new_bal, bank_card))
                bank_conn.commit()
                log_cur.execute('INSERT INTO transactions (customer, items, total, timestamp) VALUES (?,?,?,?)',
                                (user_name, ", ".join(cart_items), cart_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                log_conn.commit()
                print(f"Оплата успішна! GOOD.")
                break
            else:
                print("Помилка оплати."); break
        
        elif cmd == '?':
            shop_cur.execute('SELECT * FROM products')
            for r in shop_cur.fetchall(): print(f"ID {r[0]}: {r[1]} - {r[2]} грн")
        else:
            for i in cmd.split():
                shop_cur.execute('SELECT name, price FROM products WHERE id = ?', (i,))
                res = shop_cur.fetchone()
                if res: cart_items.append(res[0]); cart_total += res[1]

    # ЛОГИ-----------------------------------------------------------------------
    save_txt_reports(shop_conn, bank_conn)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(current_dir, "logs.txt")
    
    log_cur.execute('SELECT * FROM transactions ORDER BY id DESC LIMIT 1')
    last_entry = log_cur.fetchone()

    if last_entry:
        with open(log_file_path, "a", encoding="utf-8") as f:
            line = f"Транзакція #{last_entry[0]} | Клієнт: {last_entry[1]} | Сума: {last_entry[3]} грн | Час: {last_entry[4]}\nТовари: {last_entry[2]}\n"
            f.write(line + "-"*30 + "\n")
        print(f"\n[ ADMIN INFO ]: Звіт додано в {log_file_path}")

    for c in [shop_conn, bank_conn, log_conn]: c.close()

if __name__ == "__main__":
    run_self_checkout()