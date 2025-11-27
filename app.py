from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
import helpers
from helpers import User, admin_required
from dotenv import load_dotenv
import os
import sqlite3
from datetime import timedelta


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
CSV_FILE = "static/tech_products.csv"

#26/11/2025 -> tomorrow im going to create a new route which will actually instead just validate the order instead of having one function do all this
#create a route called something like /admin/validate_order
#it will use get requests and then with my javascript it will use fetch and instead of post, this time it will use method=get
#so my create_order function will be used to do the backend checks of the order and ensure no spam can get through, frontend will only handle the UX doing simple checks to make sure
#that everything seems ok to the user

#27/11/2025 -> I understand the general flow of how it is meant to be now, to handle any order errors with js and flask:
#> User submits form
#> js intercepts and basically pauses everything with preventDefault()
#> js does all the normal checks with verify_order
#> if its all good, then it will submit the form with a POST request to create_order
#> if not it will show the error messages and never submit it to create_order
#> it took me like 30 mins to understand this





@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("databases/logins.db") as db:
        cursor = db.cursor()
        cursor.execute('''SELECT id, username, role FROM login_deets WHERE id = ?''', (int(user_id),))
        data = cursor.fetchone()
    
    if data:
        return User(data[0], data[1], data[2])
    return None




load_dotenv()

app.secret_key = os.getenv("SECRET_KEY", "default-user-testing-key")
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('HTML/index.html')

@app.route('/login')
def login():
    return render_template('HTML/login.html')

@app.route('/homepage', methods=['GET', 'POST'])
@login_required
def home_page():
    if helpers.verify_role() == "verify_admin":
        return redirect(url_for("admin_hp"))
    return render_template('HTML/user-home-page.html', user=current_user)

@app.route("/homepage/verify")
@login_required
def verify_user_role():
    if helpers.verify_role() == "verify_admin":
        return redirect(url_for("admin_hp"))
    else:
        return redirect(url_for("home_page"))

@app.route("/homepage/admin", methods=['GET', 'POST'])
@login_required
@admin_required
def admin_hp():
    return render_template("HTML/admin-home-page.html")

@app.route("/admin/manage_admins", methods=['POST', 'GET'])
@login_required
@admin_required
def manage_admins():
    if request.is_json:
        role_user_text = request.get_json()
        admin_manager = helpers.ManageAdmins(role_user_text)
        if role_user_text['action'] == "appoint":
            valid = admin_manager.appoint_admin(current_user)
            if not valid['pass']:
                return jsonify({ 
                    "ok" : False,
                    "fieldErrors" : {valid['error_with'] : valid['error']}
                }), valid['status']

            else:
                return jsonify({
                    "ok" : True
                }        
            ), 201
        elif role_user_text['action'] == "remove":
            valid = admin_manager.remove_admin()
            if not valid['pass']:
                return jsonify({
                    "ok" : False,
                    "fieldErrors" : {valid['error_with'] : valid['error']}
                }), valid['status']
            else:
                return jsonify({ 
                    "ok" : True
                }), 201

    user_and_role = helpers.display_all_users()
    username = getattr(current_user, "username")
    return render_template("HTML/admin_manager.html", user_and_role=user_and_role, logged_in_as=username)

@app.route("/admin/create_order", methods=['POST', 'GET'])
@login_required
@admin_required
def create_order():
    total = "N/A"
    order = {'customer_name' : '', 
                'customer_address' : '', 
                'order_date' : '',
                'order_status' : '',
                'product_type' : '',
                'product_id' : '',
                'quantity_ordered' : ''}
    if request.method == "POST":
        order = {'customer_name' : request.form['c_name'], 
                 'customer_address' : request.form['c_address'], 
                 'order_date' : request.form['o_date'],
                 'order_status' : request.form['status'],
                 'product_type' : request.form['p_type'],
                 'product_id' : request.form['p_id'],
                 'quantity_ordered' : request.form['q_ordered']}
        helpers_order = helpers.CreateOrder(order, CSV_FILE)
        
        if helpers_order.verify_order_validity(order['product_type'], order['product_id']):
            print("should of passed again?")
            if helpers_order.verify_stock(order['quantity_ordered'], order['product_id']):
                print("should of passed")
                temp_total = helpers_order.calculate_total(order['quantity_ordered'], order['product_id'])
                if temp_total:
                    total = temp_total
                return render_template("HTML/create-order.html", total=total, order=order)


    return render_template("HTML/create-order.html", total=total, order=order)

@app.route("/admin/verify_order", methods=['GET'])
@login_required
@admin_required
def verify_order():
    pass
    

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products_page():
    products = helpers.display_products(CSV_FILE)
    if request.method == "POST":
        filter_option = request.form['filter']
        search_option = request.form['search']
        print(filter_option, search_option)
        filtered = helpers.sort_data(CSV_FILE, filter_option)
        searched_with_filter = helpers.search_and_filter(CSV_FILE, search_option, filter_option)
        if searched_with_filter:
            print("User is searching and filtering")
            return render_template("HTML/products.html", products=searched_with_filter[0])
        else:
            print("user only searced with filter")
            return render_template("HTML/products.html", products=filtered) 
    return render_template("HTML/products.html", products=products)




@app.route("/homepage/admin/logout", methods=['GET', 'POST'])
@login_required
@admin_required
def adm_logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/homepage/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/verify/login', methods=['POST'])
def login_form():
    if request.is_json:
        details = request.get_json()
        username = details.get("username")
        password = details.get("password")
        chkbox_val = bool(details.get("checkbox"))
        valid = helpers.auth_user(username, password)
        if valid['success']:
            user = valid['user']
            login_user(user, remember=chkbox_val)
            return jsonify({
                "ok" : True,
                "redirect" : url_for("verify_user_role")
            }), 201
        else:
            error = helpers.errors_map(valid['error'])
            return jsonify({
                "ok" : False,
                "fieldErrors" : {valid['error_with'] : error}
            }), valid['status']

@app.route('/register', methods=['GET'])
def load_sign_up():
    return render_template('HTML/sign-up.html')

@app.route('/verify/register-user', methods=['POST'])
def sign_up_form():
        if request.is_json:
            details = request.get_json()
            username = details.get("username")
            password = details.get("password")
            conf_password = details.get("confirm_password")

            valid = helpers.validate_login(username, password)
            if not valid['success']:
                error = helpers.errors_map(valid['error'])
                return jsonify({
                    "ok" : False,
                    "fieldErrors" : {valid['error_with'] : error}
                }), valid['status']
            else:
                valid = helpers.create_user(username, password, conf_password)
                
                if not valid['success']:
                    error = helpers.errors_map(valid['error'])
                    return jsonify({
                        "ok" : False,
                        "fieldErrors" : {valid['error_with'] : error}
                    }), valid['status']
            
            return jsonify({
                "ok" : True,
                "redirect" : url_for("index")
            }), 201
        else:
            
            return jsonify({
                "ok" : False,
                "error" : "Invalid JSON request"
            }), 415





if __name__ == '__main__':
    app.run(port=1000, debug=True)
