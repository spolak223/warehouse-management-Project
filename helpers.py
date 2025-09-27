import sqlite3
import bcrypt


def validate_login(username, password):
    if len(password) < 8:
        return {'success' : False, 'error' : 1, 'error_with' : 'password', 'status' : 422}
    with sqlite3.connect('databases/logins.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT username FROM login_deets''')
        data = cursor.fetchall()
        for usernames in data:
            if username == usernames[0]:
                return {'success' : False, 'error' : 2, 'error_with' : 'username', 'status' : 409}
    return {'success' : True}

def create_user(username, password, conf_password):
    if password == conf_password:
        bpassword = password.encode("utf-8")
        hashed_pass = bcrypt.hashpw(bpassword, bcrypt.gensalt())
        with sqlite3.connect("databases/logins.db") as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO login_deets(username, password) VALUES (?, ?)""", (username, hashed_pass))
            db.commit()
            cursor.close()
        return {'success' : True}
    else:
        return {'success' : False, 'error' : 3, 'error_with' : 'confirm_password', 'status' : 422}

def validate_user():
    pass

def errors_map(error_number):
    errors = {
        1 : "Password too short",
        2 : "Username is already taken",
        3 : "Passwords do not match"
    }
    return errors[error_number]

    


