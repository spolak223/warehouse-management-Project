from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
import helpers
from helpers import User
from dotenv import load_dotenv
import os
import sqlite3


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    #print(user_id)
    with sqlite3.connect("databases/logins.db") as db:
        cursor = db.cursor()
        cursor.execute('''SELECT id, username FROM login_deets WHERE id = ?''', (int(user_id),))
        data = cursor.fetchone()
    
    if data:
        return User(data[0], data[1])
    return None



load_dotenv()

app.secret_key = os.getenv("SECRET_KEY", "default-user-testing-key")

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/homepage')
@login_required
def home_page():
    return render_template('home-page.html', user=current_user)


@app.route('/homepage/logout', methods=['POST', 'GET'])
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
        valid = helpers.auth_user(username, password)
        if valid['success']:
            user = valid['user']
            login_user(user)
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
    return render_template('sign-up.html')

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
