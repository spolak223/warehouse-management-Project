import sqlite3
import bcrypt
from flask_login import UserMixin
import csv
import pandas
import duckdb

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


def validate_login(username, password):
    if len(password) < 8:
        return {'success' : False, 'error' : 1, 'error_with' : 'password', 'status' : 422}
    with sqlite3.connect('databases/logins.db') as db:
        cursor = db.cursor()
        cursor.execute('''SELECT 1 FROM login_deets WHERE username = ? ''', (username,))
        data = cursor.fetchone()
        if data:
            return {'success' : False, 'error' : 2, 'error_with' : 'username', 'status' : 409}
    return {'success' : True}

def create_user(username, password, conf_password):
    if password == conf_password:
        bpassword = password.encode("utf-8")
        hashed_pass = bcrypt.hashpw(bpassword, bcrypt.gensalt())
        with sqlite3.connect("databases/logins.db") as db:
            cursor = db.cursor()
            cursor.execute("""INSERT INTO login_deets(username, password, ROLE) VALUES (?, ?, ?)""", (username, hashed_pass, "user"))
            db.commit()
            cursor.close()
        return {'success' : True}
    else:
        return {'success' : False, 'error' : 3, 'error_with' : 'confirm_password', 'status' : 422}


def errors_map(error_number):
    errors = {
        1 : "Password too short",
        2 : "Username is already taken",
        3 : "Passwords do not match",
        4 : "Login details are incorrect!"
    }
    return errors[error_number]

def auth_user(username, password):
    with sqlite3.connect("databases/logins.db") as db:
        cursor = db.cursor()
        cursor.execute('''SELECT username, password, id FROM login_deets WHERE username = ?''', (username,))
        data = cursor.fetchone()
        if data:
            if bcrypt.checkpw(password.encode(), data[1]):
                db_user, _, db_id = data
                return {'success' : True,'user' : User(db_id, db_user)}

    return {'success' : False, 'error' : 4, 'error_with' : 'login_details', 'status' : 401}

def create_admin(username, password):
    pass



def display_products(csv_file):
    data = pandas.read_csv(csv_file)
    
    return data.to_dict(orient="records")

def sort_data(csv_file, order_by):
    if order_by == "H2LPrice":
        query = f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Sale Price" DESC'
        return duckdb.sql(query).df().to_dict('records')







    


    


