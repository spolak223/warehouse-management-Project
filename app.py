from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import helpers

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home_page():
    return render_template('index.html')

@app.route('/register-user', methods=['GET', 'POST'])
def sign_up_page():
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        conf_password = request.form['conf-password']
        helpers.create_user(user, password, conf_password)
        return redirect(url_for('home_page'))
    return render_template('sign-up.html')




if __name__ == '__main__':
    app.run(port=1000, debug=True)
