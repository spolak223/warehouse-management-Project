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
CSV_FILE = "static/ComputerSales.csv"

@login_manager.user_loader
def load_user(user_id):
    with sqlite3.connect("databases/logins.db") as db:
        cursor = db.cursor()
        cursor.execute('''SELECT id, username, role FROM login_deets WHERE id = ?''', (int(user_id),))
        data = cursor.fetchone()
    
    if data:
        return User(data[0], data[1], data[2])
    return None


#07/10/2025 -> Tomorrow, add in filtering by all specified values, probably do this in SQL --> DONE
#if possible -> Also add in search, I'll have to do this through SQL it'll be easiest. -> DONE (14/10/25)
#IF i absolutely manage to try also adding in the admin management thing, will be a hard task -> partially done heres what i need to do next:
# > make it so that admins have their own homepage / desktop -> DONE(well partially still need to create interface for it)
# > allow an admin to appoint another admin -> DONE
# > create admin only resources such as disabling accounts and etc.

#for tomorrow -> 22/10/25 - make it so that each row is clickable to appoint / remove admins -> i dont wanna make 2 identical html files for this and the only difference is one button :/

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

@app.route("/admin/appoint_admin", methods=['GET', 'POST'])
@login_required
@admin_required
def appoint_admins():
    if request.method == "POST":
        usr_to_admin = request.form.get("choose_user", False)
        helpers.manage_admins(usr_to_admin, "appoint")
    user_and_role = helpers.display_all_users()
    username = getattr(current_user, "username")
    
    return render_template("HTML/appoint_admins_page.html", user_and_role=user_and_role, logged_in_as=username)

@app.route("/admin/remove_admin", methods=['POST', 'GET'])
@login_required
@admin_required
def remove_admins():
    user_and_role = helpers.display_all_users()
    username = getattr(current_user, "username")
    return render_template("HTML/remove_admins_page.html", user_and_role=user_and_role, logged_in_as=username)
    

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products_page():
    products = helpers.display_products(CSV_FILE)
    if request.method == "POST":
        filter_option = request.form['filter']
        search_option = request.form['search']
        searched = helpers.searching(CSV_FILE, search_option)
        if searched:
            return render_template("HTML/products.html", products=searched[0])
        filtered = helpers.sort_data(CSV_FILE, filter_option)
        return render_template("HTML/products.html", products=filtered) 
    return render_template("HTML/products.html", products=products)




@app.route("/homepage/admin/logout", methods=['GET', 'POST'])#
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
