import sqlite3
import bcrypt
import pandas
import duckdb
from functools import wraps
from flask_login import current_user, UserMixin
from flask import abort

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


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
        cursor.execute('''SELECT username, password, id, role FROM login_deets WHERE username = ?''', (username,))
        data = cursor.fetchone()
        if data:
            if bcrypt.checkpw(password.encode(), data[1]):
                db_user, _, db_id, db_role = data
                return {'success' : True,'user' : User(db_id, db_user, db_role)}

    return {'success' : False, 'error' : 4, 'error_with' : 'login_details', 'status' : 401}

def create_admin(username, password):
    pass



def display_products(csv_file):
    data = pandas.read_csv(csv_file)
    
    return data.to_dict(orient="records")

def sort_data(csv_file, order_by):
    filter_dict = {'H2LPrice' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Sale Price" DESC',
                   'L2HPrice' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Sale Price" ASC',
                   'H2LYear' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Year" DESC', 
                   'L2HYear' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Year" ASC',
                   'H2LID' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Sale ID" DESC', 
                   'L2HID' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Sale ID" ASC'}
    return duckdb.sql(filter_dict[order_by]).df().to_dict("records")

def searching( csv_file, user_inp=None):
    if user_inp:
        search = f"%{user_inp}%"
        query = f'SELECT * FROM read_csv_auto("{csv_file}") WHERE "Product ID" ILIKE ?'
        return duckdb.execute(query, [search]).df().to_dict("records"), True
    else:
        return False
    
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if getattr(current_user, "role", "admin") != "admin":
            return abort(403)
        return func(*args, **kwargs)
    return wrapper

def verify_role():
    if getattr(current_user, "role", "admin") == "admin":
        return "verify_admin"
    return None

def manage_admins(username, action):
    with sqlite3.connect("databases/logins.db") as file:
        if action == "appoint":
            cursor = file.cursor()
            cursor.execute("""UPDATE login_deets SET role = 'admin' WHERE username = ?""", (username,))
            cursor.close()
            return
        elif action == "remove":
            cusor = file.cursor()
            cursor.execute("""UPDATE login_deets SET role = 'user WHERE username = ?""", (username, ))
            cursor.close()
            return


    

def display_all_users():
    with sqlite3.connect("databases/logins.db") as file:
        cursor = file.cursor()
        cursor.execute("""SELECT username, role FROM login_deets""")
        data = cursor.fetchall()
    return data




        
            
    








    


    


