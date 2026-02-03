import sqlite3
import customtkinter as ctk
from datetime import datetime
import os

from database_setup import setup_databases
from file_reports import save_txt_reports

class KassaPOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Start databases
        self.shop_conn, self.bank_conn, self.log_conn = setup_databases()
        
        self.title("POS Terminal")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))
        
        ctk.set_appearance_mode("dark")

        self.cart = []
        self.total = 0.0
        self.user_name = "Guest"

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self.create_left_panel()
        self.create_right_panel()
        
    def create_left_panel(self):
        left_frame = ctk.CTkFrame(self, corner_radius=0)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Staff Auth
        auth_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        auth_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(auth_frame, text="Code:", font=("Arial", 16)).pack(side="left", padx=5)
        self.staff_entry = ctk.CTkEntry(auth_frame, width=100)
        self.staff_entry.pack(side="left", padx=5)
        ctk.CTkButton(auth_frame, text="OK", width=40, command=self.login_staff).pack(side="left")

        self.label_user = ctk.CTkLabel(left_frame, text=f"Cashier: {self.user_name}", font=("Arial", 14, "bold"))
        self.label_user.pack()

        # Receipt View
        self.receipt_view = ctk.CTkTextbox(left_frame, font=("Courier New", 14))
        self.receipt_view.pack(expand=True, fill="both", padx=10, pady=10)
        self.receipt_view.insert("1.0", f"{'ITEM':<20} {'PRICE':>10}\n" + "="*35 + "\n")

        self.label_sum = ctk.CTkLabel(left_frame, text="TOTAL: 0.00 UAH", font=("Arial", 28, "bold"), text_color="#2ecc71")
        self.label_sum.pack(pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=10)
        ctk.CTkButton(btn_frame, text="CLEAR", fg_color="#e74c3c", command=self.clear_cart).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="PAY", fg_color="#27ae60", height=50, font=("Arial", 18, "bold"), command=self.process_pay).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="EXIT", fg_color="#95a5a6", command=self.on_exit).pack(side="left", expand=True, padx=5)

    def create_right_panel(self):
        right_container = ctk.CTkFrame(self, corner_radius=0)
        right_container.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
        
        items_frame = ctk.CTkScrollableFrame(right_container, corner_radius=0)
        items_frame.pack(expand=True, fill="both", padx=2, pady=2)

        # Load products
        cur = self.shop_conn.cursor()
        cur.execute('SELECT name, price FROM products')
        products = cur.fetchall()

        for i, (name, price) in enumerate(products):
            btn = ctk.CTkButton(items_frame, text=f"{name}\n{price} UAH", width=180, height=100,
                                font=("Arial", 14, "bold"), command=lambda n=name, p=price: self.add_item(n, p))
            btn.grid(row=i//3, column=i%3, padx=10, pady=10)

        # Payment Zone
        bank_frame = ctk.CTkFrame(right_container, height=80)
        bank_frame.pack(fill="x", padx=10, pady=20)
        ctk.CTkLabel(bank_frame, text="CARD:", font=("Arial", 14, "bold")).pack(side="left", padx=15)
        self.card_entry = ctk.CTkEntry(bank_frame, placeholder_text="Card Number", width=300, height=40)
        self.card_entry.pack(side="left", padx=10, pady=10)

    def login_staff(self):
        code = self.staff_entry.get().strip()
        cur = self.shop_conn.cursor()
        cur.execute('SELECT owner FROM loyalty_cards WHERE card_id = ?', (code,))
        res = cur.fetchone()
        self.user_name = res[0] if res else "Unknown"
        self.label_user.configure(text=f"Cashier: {self.user_name}")

    def add_item(self, name, price):
        self.cart.append(name)
        self.total += price
        self.receipt_view.insert("end", f"{name:<20} {price:>10.2f}\n")
        self.label_sum.configure(text=f"TOTAL: {self.total:.2f} UAH")
        self.receipt_view.see("end")

    def clear_cart(self):
        self.cart = []
        self.total = 0.0
        self.receipt_view.delete("3.0", "end")
        self.label_sum.configure(text="TOTAL: 0.00 UAH")

    def process_pay(self):
        if not self.cart: return
        card = self.card_entry.get().strip()
        
        bank_cur = self.bank_conn.cursor()
        bank_cur.execute('SELECT balance FROM accounts WHERE card_number = ?', (card,))
        acc = bank_cur.fetchone()

        if acc and acc[0] >= self.total:
            new_bal = acc[0] - self.total
            bank_cur.execute('UPDATE accounts SET balance = ? WHERE card_number = ?', (new_bal, card))
            self.bank_conn.commit()
            
            log_cur = self.log_conn.cursor()
            log_cur.execute('INSERT INTO transactions (customer, items, total, timestamp) VALUES (?,?,?,?)',
                          (self.user_name, ", ".join(self.cart), self.total, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.log_conn.commit()
            
            save_txt_reports(self.shop_conn, self.bank_conn, self.log_conn)
            
            self.receipt_view.insert("end", "\n" + "-"*35 + "\nPAYMENT SUCCESSFUL!\nReports updated.\n")
            self.clear_cart()
            self.card_entry.delete(0, 'end')
        else:
            self.receipt_view.insert("end", "\nERROR: PAYMENT DECLINED!\n")

    def on_exit(self):
        for conn in [self.shop_conn, self.bank_conn, self.log_conn]:
            conn.close()
        self.quit()

if __name__ == "__main__":
    app = KassaPOS()
    app.mainloop()