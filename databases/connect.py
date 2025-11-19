import sqlite3

try:
    with sqlite3.connect("databases/logins.db") as conn:
        print("Databse has been created maybe?")
except sqlite3.OperationalError as e:
    print("Ok database has failed now", e)


with sqlite3.connect("logins.db") as conn:
    cursor = conn.cursor()
    cursor.execute("" \
    "CREATE TABLE IF NOT EXISTS login_deets(" \
    "id INTEGER PRIMARY KEY," \
    "username TEXT NOT NULL UNIQUE," \
    "password TEXT NOT NULL, " \
    "ROLE TEXT NOT NULL)")
    conn.commit()


with sqlite3.connect("orders.db") as orders_DB:
    cursor = orders_DB.cursor()
    cursor.execute("" \
    "CREATE TABLE IF NOT EXISTS orders(" \
    "order_id INTEGER PRIMARY KEY," \
    "customer_name TEXT," \
    "customer_address TEXT," \
    "order_date DATE," \
    "status TEXT," \
    "subtotal REAL NOT NULL," \
    "vat REAL NOT NULL," \
    "total REAL NOT NULL)")
    orders_DB.commit()
    orders_DB.close()

