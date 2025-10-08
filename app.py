from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
import helpers
from helpers import User
from dotenv import load_dotenv
import os
import sqlite3
import json
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
        cursor.execute('''SELECT id, username FROM login_deets WHERE id = ?''', (int(user_id),))
        data = cursor.fetchone()
    
    if data:
        return User(data[0], data[1])
    return None


#07/10/2025 -> Tomorrow, add in filtering by all specified values, probably do this in SQL
#if possible -> Also add in search, I'll have to do this through SQL it'll be easiest. 
#IF i absolutely manage to try also adding in the admin management thing, will be a hard task

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
    return render_template('HTML/home-page.html', user=current_user)

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products_page():
    products = helpers.display_products(CSV_FILE)
    if request.method == "POST":
        filter_option = request.form['filter']
        
        if filter_option == "H2LPrice":
            print("Here")
            hp = helpers.sort_data(CSV_FILE, filter_option)
            print(hp)
            return render_template("HTML/products.html", products=hp)
    print("Nvm im here")    
    return render_template("HTML/products.html", products=products)




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
                "redirect" : url_for("home_page")
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
