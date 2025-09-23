import sqlite3
import bcrypt


def validate_login(username, password):
    pass

def create_user(username, password, conf_password):
    if password == conf_password:
        bpassword = password.encode("utf-8")
        hashed_pass = bcrypt.hashpw(bpassword, bcrypt.gensalt())
        with sqlite3.connect("databases/logins.db") as db:
            cursor = db.cursor()
        cursor.execute("""INSERT INTO login_deets(username, password) VALUES (?, ?)""", (username, hashed_pass))
        db.commit()
        cursor.close()

    


