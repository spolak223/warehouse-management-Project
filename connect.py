import sqlite3

try:
    with sqlite3.connect("databases/logins.db") as conn:
        print("Databse has been created maybe?")
except sqlite3.OperationalError as e:
    print("Ok database has failed now", e)


with sqlite3.connect("logins.db") as conn:
    cursor = conn.cursor()
    cursor.execute("" \
    "CREATE TABLE login_deets(" \
    "id INTEGER PRIMARY KEY," \
    "username TEXT NOT NULL UNIQUE," \
    "password TEXT NOT NULL)")
    conn.commit()

