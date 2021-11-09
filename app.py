from flask import Flask, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import pymysql
import re
import datetime
import io
import cv2
import os
from config import Config
from dotenv import load_dotenv
import numpy as np
from pymysql.cursors import Cursor
import pytesseract
from PIL import Image
from post_ocr import post_ocr
from fuzzy import get_details
from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mysql = MySQL()

app.config.from_object(Config)

# MySQL configurations
load_dotenv()
app.config['MYSQL_DATABASE_USER'] = os.environ.get('MYSQL_DATABASE_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('MYSQL_DATABASE_DB')
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('MYSQL_DATABASE_HOST')
# app.config['MYSQL_DATABASE_USER'] = 'admin'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'plaser2021'
# app.config['MYSQL_DATABASE_DB'] = 'plaser'
# app.config['MYSQL_DATABASE_HOST'] = 'plaser-test.cp4vsdtdjf2c.ap-south-1.rds.amazonaws.com'
mysql.init_app(app)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():
    if request.method == 'POST':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        start_time = datetime.datetime.now()
        img1 = request.files['file'].read()
       # print("Hello")
        img = Image.open(io.BytesIO(img1))
    #     # Rescaling the image
        img=np.array(img)
        img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC) 

    # Converting image to gray-scale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Applying dilation and erosion to remove the noise
        kernel = np.ones((1, 1), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)

        # Apply threshold to get image with only black and white
        list_of_methods = ["GaussianBlur", "bilateralFilter", "medianBlur", "GaussianBlurAdaptive", "bilateralFilterAdaptive", "medianBlurAdaptive"]
        img = apply_threshold(img, list_of_methods[3])
        # scanned_text = pytesseract.image_to_string(Image.open(io.BytesIO(img)))
        scanned_text = pytesseract.image_to_string(img)

        print("Found data:", scanned_text)
        ingredient_list=post_ocr(scanned_text)
        final_list=get_details(ingredient_list)
        # session['data'] = {
        #     "text": scanned_text,
        #     "time": str((datetime.datetime.now() - start_time).total_seconds())
        # }
        return render_template("result.html",result=final_list)

def show_products(id):

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    get_products = "SELECT product,expiry,product_id FROM products where id = '%d'" % (id)
    cursor.execute(get_products)
    results = cursor.fetchall()
    
    dic = {}
    for name,exp,p_id in results:
        dic[p_id] = [name,exp]
    return dic

@app.route('/dashboard')
def scan():
    dic = show_products(id)
    return render_template("profile.html")

@app.route('/new_product',methods=['GET', 'POST'])
def add_product():

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method== "POST":
        prod_name=request.form['name']
        expiry_date=request.form['date']
        # add query to to insert into db

        prod_to_add = "INTERT INTO products(id,product,expiry,product_id) VALUES (%s,%s,%s,NULL)",(id,prod_name,expiry_date)
        cursor.execute(prod_to_add)

        return redirect('/dashboard')
    else:
        return render_template("new_product.html")

@app.route('/product/edit/<int:id>')
def edit_product(id):
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    prod_to_edit= "SELECT product,expiry,product_id from products where product_id = '%d'" % (id)
    cursor.execute(prod_to_edit)

    if request.method== 'POST':
        prod_name=request.form['name']
        expiry_date=request.form['date']
        
        prod_to_update = "UPDATE PRODUCTS SET product = '%s', expiry = '%d'" % (prod_name,expiry_date)
        cursor.execute(prod_to_update)

        return redirect('/dashboard')   
    else: 
        return render_template("edit_product.html",result=prod_to_edit)



def apply_threshold(img, argument):
    # Applying blur (each of which has its pros and cons, however,
    # median blur and bilateral filter usually perform better than gaussian blur.):

    switcher = {
        "GaussianBlur": cv2.threshold(cv2.GaussianBlur(img, (5, 5), 0), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        "bilateralFilter": cv2.threshold(cv2.bilateralFilter(img, 5, 75, 75), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        "medianBlur": cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
        "GaussianBlurAdaptive": cv2.adaptiveThreshold(cv2.GaussianBlur(img, (5, 5), 0), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        "bilateralFilterAdaptive": cv2.adaptiveThreshold(cv2.bilateralFilter(img, 9, 75, 75), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2),
        "medianBlurAdaptive": cv2.adaptiveThreshold(cv2.medianBlur(img, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    }
    return switcher.get(argument, "Invalid method")



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
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    app.run(debug=True)