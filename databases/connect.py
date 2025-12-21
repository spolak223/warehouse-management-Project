import sqlite3

#once databases have been created, feel free to comment out the ones you don't need

with sqlite3.connect("databases/logins.db") as conn:
    cursor = conn.cursor()
    cursor.execute("" \
    "CREATE TABLE IF NOT EXISTS login_deets(" \
    "id INTEGER PRIMARY KEY," \
    "username TEXT NOT NULL UNIQUE," \
    "password TEXT NOT NULL, " \
    "ROLE TEXT NOT NULL)")
    conn.commit()


with sqlite3.connect("databases/manage_orders.db") as business_DB:
    cursor = business_DB.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("" \
    "CREATE TABLE IF NOT EXISTS business(" \
    "business_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL," \
    "business_name TEXT," \
    "business_address TEXT)")
    business_DB.commit()
    cursor.close()


with sqlite3.connect("databases/manage_orders.db") as orders_DB:
    cursor = orders_DB.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("" \
    "CREATE TABLE IF NOT EXISTS orders(" \
    "order_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL," \
    "business_id INTEGER NOT NULL," \
    "order_date DATE," \
    "deadline_date DATE," \
    "product_id TEXT NOT NULL," \
    "order_quantity INTEGER NOT NULL," \
    "status TEXT," \
    "total REAL NOT NULL," \
    "FOREIGN KEY(business_id) REFERENCES business(business_id))")
    orders_DB.commit()
    cursor.close()

with sqlite3.connect("databases/manage_orders.db") as invoices_db:
    cursor = invoices_db.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.execute("CREATE TABLE IF NOT EXISTS invoices(" \
    "invoice_id INTEGER PRIMARY KEY AUTOINCREMENT," \
    "order_id INTEGER UNIQUE NOT NULL," \
    "issue_date DATE," \
    "deadline_date DATE," \
    "date_fulfilled DATE," \
    "subtotal REAL NOT NULL," \
    "VAT INTEGER NOT NULL," \
    "FOREIGN KEY(order_id) REFERENCES orders(order_id))")
    invoices_db.commit()
    cursor.close()

