from flask import Flask, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import pymysql
import re

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '10102000'
app.config['MYSQL_DATABASE_DB'] = 'plaser'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/s')
def price():
    return render_template("scanner.html")

@app.route('/new',methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    msg = ''
    # print(request.form)
    if request.method == 'POST' and 'password' in request.form:
        # print(2)
        fullname = request.form['name']
        email = request.form['email']
        mobile = request.form['Mobile No.']
        password = request.form['password']

        cursor.execute('SELECT * FROM userdetails WHERE email = %s', (email))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO userdetails(id,email,mobile,fullname,password) VALUES (NULL, %s, %s, %s, %s)', (email, mobile, fullname, password))
            conn.commit()

            msg = 'You have successfully registered!'
    elif request.method == 'POST' and 'lpassword' in request.form:
        # print(3)
        email = request.form['lemail']
        password = request.form['lpassword']
        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM userdetails WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            msg = "Sucessfully logged-In"
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    return render_template("login.html",msg=msg)

if __name__ == '__main__':
    app.run(debug=True)