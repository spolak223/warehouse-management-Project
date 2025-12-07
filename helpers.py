import sqlite3
import bcrypt
import pandas
import duckdb
from functools import wraps
from flask_login import current_user, UserMixin
from flask import abort
from datetime import datetime, date

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role


class ManageAdmins():
    def __init__(self, text):
        self.text = text
        self.user_and_role = self.text['user_and_role'].split()
         
        

    def appoint_admin(self, current_user):
        print(f"this? : {getattr(current_user, "username")}")
        if self.user_and_role[1].strip() == "admin":
            return {"pass": False, "error" : "User is already admin", "status" : 405, "error_with" : "appointing"}
        elif getattr(current_user, "username") == self.user_and_role[0]:
            return {"pass" : False, "error" : "Cannot change your own roles!", "status" : 405, "error_with" : "appointing"}
        else:
            with sqlite3.connect("databases/logins.db") as file:
                cursor = file.cursor()
                cursor.execute("""UPDATE login_deets SET role = 'admin' WHERE username = ?""", (self.user_and_role[0],))
                cursor.close()
            return {"pass" : True}

    def remove_admin(self):
        if self.user_and_role[1].strip() == "user":
            return {"pass" : False, "error" : "User is not an admin", "status" : 405, "error_with" : "removing"}
        elif getattr(current_user, "username") == self.user_and_role[0]:
            return {"pass" : False, "error" : "Cannot change your own roles!", "status" : 405, "error_with" : "removing"}
        else:
            with sqlite3.connect("databases/logins.db") as file:
                cursor = file.cursor()
                cursor.execute("""UPDATE login_deets SET role = 'user' WHERE username = ?""", (self.user_and_role[0], ))
                cursor.close()
            
            return {"pass" : True}
        

    def create_admin(self):
        pass

class CreateOrder():
    def __init__(self, CSV_FILE, order=None, order_frontend=None):
        self.order = order
        self.CSV_FILE = CSV_FILE
        self.VAT = 1.2
        self.order_frontend = order_frontend


    def verify_frontend(self):
        for _, value in self.order_frontend.items():
            if value.strip() == "":
                return {"error_with" : "Missing field/s!"}
        
            
        if int(self.order_frontend["qty"]) <= 0:
            return {"error_with" : "Quantity cannot be less than or equal to 0!"}
        else:
            query = f"SELECT SKU, Category, Stock FROM read_csv_auto('{self.CSV_FILE}') WHERE SKU = ? AND Category = ?"
            request = duckdb.execute(query, [self.order_frontend['sku'], self.order_frontend['type']]).df().to_dict("records")
            if not request:
                return {"error_with" : "Orders' SKU code does not match the type of the product!"}
            elif request[0]['Stock'] < int(self.order_frontend["qty"]):
                return {"error_with" : "The ordered quantity is greater than what is available!"}
            
        date_of_order = datetime.strptime(self.order_frontend['date'], '%Y-%m-%d').date()
        todays_date = date.today()


        if date_of_order < todays_date:
            return {"error_with" : "Order cannot be placed in the past!"}
        return True
    
    


    def verify_order_validity(self, product_type, SKU_code):
        if self.order['quantity_ordered']:
            if int(self.order['quantity_ordered']) != 0:
                query = f"SELECT SKU, Category, Stock FROM read_csv_auto('{self.CSV_FILE}') WHERE SKU = ? AND Category = ?"
                request = duckdb.execute(query, [SKU_code, product_type]).df().to_dict("records")
                if not request:
                    return False
                elif request[0]['Stock'] < int(self.order['quantity_ordered']):
                    return False
                for _, value in self.order.items():
                    if value.strip() == "":
                        return False
                    
                date_of_order = datetime.strptime(self.order['order_date'], '%Y-%m-%d').date()
                todays_date = date.today()

                if date_of_order < todays_date:
                    return False
                return True
        return False
        
        


    def add_order_to_db(self, total):
        if self.order['order_status'] == "Completed":
            #first if the business hasn't been already created, insert it, otherwise, just add it normally
            with sqlite3.connect("databases/manage_orders.db") as orders:
                cursor = orders.cursor()
                cursor.execute("SELECT business_id FROM business WHERE business_name = ?", (self.order['customer_name'],))
                valid_business_id = cursor.fetchone()
                if valid_business_id:
                    #handle orders with existing businesses
                    pass
                else:
                    cursor.execute("INSERT INTO business(business_name, business_address) VALUES(?, ?)", (self.order['customer_name'], self.order['customer_address'], ))
                    customer_business_id = cursor.lastrowid
                    cursor.execute("INSERT INTO orders(business_id, order_date, product_id, order_quantity, status, total) VALUES(?, ?, ?, ?, ?, ?)", 
                                   (customer_business_id, 
                                    self.order['order_date'], 
                                    self.order['product_id'], 
                                    self.order['quantity_ordered'], 
                                    self.order['order_status'], 
                                    total, ))
                    customer_order_id = cursor.lastrowid
                    cursor.execute("INSERT INTO invoices(order_id, date_fulfilled, subtotal, VAT) VALUES(?, ? , ?, ?)", (customer_order_id, datetime.today().strftime('%Y-%m-%d'), self.subtotal, 20), )
                    

        else:
            #handle orders with uncompleted payments
            pass
            

    def verify_stock(self, order_qty, SKU_code):
        query = f"SELECT Stock FROM read_csv_auto('{self.CSV_FILE}') WHERE SKU = ?"
        request = duckdb.execute(query, [SKU_code]).df().to_dict("records")
        if request:
            if request[0]['Stock'] < int(order_qty):
                return {"error" : "Current order of stock exceeds available stock!"}, False
        return {"error" : False}
        

    def calculate_total(self, qty_ordered, SKU_code):
        query = f"SELECT Price FROM read_csv_auto('{self.CSV_FILE}') WHERE SKU = ?"
        request = duckdb.execute(query, [SKU_code]).df().to_dict("records")
        if request:
            self.subtotal = float(request[0]['Price']) * int(qty_ordered)
            total = self.subtotal * self.VAT
            return round(total, 2)




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




def display_products(csv_file):
    data = pandas.read_csv(csv_file)
    
    return data.to_dict(orient="records")

def sort_data(csv_file, order_by):
    filter_dict = {'H2LPrice' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Price" DESC',
                   'L2HPrice' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Price" ASC',
                   'H2LName' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Name" DESC', 
                   'L2HName' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Name" ASC',
                   'H2LStock' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Stock" DESC', 
                   'L2HStock' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "Stock" ASC',
                   'H2LID' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "ID" DESC',
                   'L2HID' : f'SELECT * FROM read_csv_auto("{csv_file}") ORDER BY "ID" ASC'}
    return duckdb.sql(filter_dict[order_by]).df().to_dict("records")

def search_and_filter(csv_file, user_inp, order_by):
    if user_inp and order_by:
        print("function should be working!")
        filter_dict = {'H2LPrice' : "Price DESC",
                    'L2HPrice' : "Price ASC",
                    'H2LName' : "Name DESC",
                    'L2HName' : "Name ASC",
                    'H2LStock' : "Stock DESC",
                    'L2HStock' : "Stock ASC",
                    'H2LID' : "ID DESC",
                    'L2HID' : "ID ASC"}
        order_value = filter_dict[order_by]
        search = f"%{user_inp}%"
        query = f'''SELECT * FROM read_csv_auto("{csv_file}") WHERE "SKU" ILIKE ? OR "Name" ILIKE ? ORDER BY {order_value}'''
        return duckdb.execute(query, [search, search]).df().to_dict("records"), True
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


def display_all_users():
    with sqlite3.connect("databases/logins.db") as file:
        cursor = file.cursor()
        cursor.execute("""SELECT username, role FROM login_deets""")
        data = cursor.fetchall()
    return data



    
    








        
            
    








    


    


