from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')




if __name__ == '__main__':
    app.run(port=1000, debug=True)
