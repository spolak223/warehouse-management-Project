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

#done
#next create a view orders and invoices page, then im going to need to give the admin user the option to edit it and etc.






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
        helpers_order = helpers.CreateOrder(CSV_FILE, order)
        print(order)
        
        if helpers_order.verify_order_validity(order['product_type'], order['product_id']):
            if helpers_order.verify_stock(order['quantity_ordered'], order['product_id']):
                temp_total = helpers_order.calculate_total(order['quantity_ordered'], order['product_id'])
                if temp_total:
                    total = temp_total
                    helpers_order.add_order_to_db(total)
                return render_template("HTML/create-order.html", total=total, order=order)


    return render_template("HTML/create-order.html", total=total, order=order)

@app.route("/admin/verify_order", methods=['GET'])
@login_required
@admin_required
def verify_order():
    product_id = request.args.get("sku")
    order_qty = request.args.get("qty")
    order_type = request.args.get("type")
    order_date = request.args.get("date")
    order = {"sku" : product_id,
             "qty" : order_qty,
             "type" : order_type,
             "date" : order_date}
    verify_order_helpers = helpers.CreateOrder(CSV_FILE, None, order)
    check_frontend = verify_order_helpers.verify_frontend()
    if check_frontend == True:
        return jsonify({
            "ok" : True
        }), 201
    else:
        return jsonify({
            "ok" : False,
            "fieldErrors" : {"error" : check_frontend['error_with']}
        })
    

@app.route("/admin/manage_order_invoice", methods=['POST', 'GET'])
@login_required
@admin_required
def orders_and_invoices_editor():
    #this is the way I'm going to want to display order addresses
    orders_invoice_helper = helpers.CreateOrder(None, None, None)
    o_and_i = orders_invoice_helper.display_businesses()
    #test = orders_invoice_helper.add_business_details()
    #print(test)


    return render_template("HTML/order_invoice_mnger.html", data=o_and_i)

@app.route("/admin/view_order/<int:business_id>", methods=['POST', 'GET'])
@login_required
@admin_required
def view_order(business_id):
    helper_class = helpers.CreateOrder(None, None, None)
    business_details = helper_class.add_business_details(business_id)
    business_address = business_details[2]
    address_helper = helper_class.manage_address(business_address)
    print(address_helper)
    
    order_details = {"order_id" : business_details[0],
                     "business_name" : business_details[1],
                     "num_and_street" : None,
                     "city" : None,
                     "order_date" : business_details[3]}
    


    return render_template("HTML/pick_note.html", order_details = order_details)
    

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
