# POS Terminal System

A modern Point of Sale (POS) terminal application built with Python. This system simulates a grocery store checkout process, including staff authorization, inventory management, and bank transaction processing.



## Features

* **Full-Screen GUI**: Professional cashier interface built with **CustomTkinter**.
* **Dual-Panel Design**: 
    * **Left Panel**: Real-time receipt generation, staff login, and payment controls.
    * **Right Panel**: Interactive product grid with auto-scrolling and card entry.
* **Database Integration**: Uses three separate SQLite databases managed by the **sqlite3** library.
* **Auto-Reporting**: Automatically generates .txt reports for inventory, customers, and transactions after every purchase.
* **Multilingual Support**: Fully translated into English.

## Tech Stack

* **Language**: Python 3.x
* **GUI Library**: CustomTkinter
* **Database Engine**: **SQLite3** (Built-in Python library for SQL database management)
* **Storage**: Local .db files and .txt report files

## Project Structure

* **main_gui.py**: The core application containing the graphical interface logic and event handling.
* **database_setup.py**: Script to initialize the SQLite environment, create tables, and populate them with initial data.
* **file_reports.py**: Specialized logic for exporting database records into human-readable text formats.
* **shop_server.db**: SQLite database storing product details and loyalty card information.
* **bank_server.db**: SQLite database simulating a banking system with account numbers and balances.
* **logs_server.db**: SQLite database used for recording transaction history and timestamps.

## Database Management with SQLite3

The system leverages the **sqlite3** library to ensure data persistence without the need for an external server. It is a standard Python library that handles relational data through SQL queries, ensures transaction integrity during balance updates, and allows the application to remain lightweight and portable.

## Getting Started

### Prerequisites
Ensure you have Python installed. The **sqlite3** library is included in the Python standard library. You will only need to install the **CustomTkinter** library:

pip install customtkinter
Installation and Execution

    Download all project files into a single directory.

    Run the main application script:
    python main_gui.py

How to Use
Staff Authorization: Enter the staff code in the top-left field and press OK to identify the cashier.
    Adding Items: Click on the product buttons in the right panel. Each click adds the item to the digital receipt and updates the total.
    Processing Payment: Enter a card number in the CARD field and press PAY. The system will verify the balance in bank_server.db.
    Generating Reports: After a successful transaction, the system automatically triggers save_txt_reports() to update all local .txt files.
    Exit: Press the EXIT button or the Escape key to close the application.
