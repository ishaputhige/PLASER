from flask import Flask, request, render_template, redirect, url_for, session,flash
from flask_session import Session
from flaskext.mysql import MySQL
import pymysql
import re
import datetime
import time
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
from datetime import datetime
import pandas as pd
from recommendations import categories,brands,products,recommend
from reminders import reminder

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
mysql = MySQL()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
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

@app.cli.command("testing")
def testing():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("select * from products")
    results = cursor.fetchall()
    now = datetime.now()
    date_now = now.strftime("%Y-%m-%d")
    # print(datetime.date(date_now-str(results[1]["expiry"])))
    # print(len(results))
    for i in range(len(results)):
        date_format = "%Y-%m-%d"
        # print(results[1]["expiry"])
        a = datetime.strptime(str(results[i]["expiry"]), date_format)
        b = datetime.strptime(date_now, date_format)
        delta = a - b
        print(delta.days) # that's it
        if delta.days == 14 or delta.days == 7 or delta.days == 1:
            cursor.execute("select * from userdetails where id = %s",results[i]["id"])
            results2 = cursor.fetchone()
            print(results2)
            reminder(results2["fullname"],results[i]["product"],results[i]["expiry"],results2["email"],results2["mobile"])
    return "Hi"

@app.route('/scanner', methods=['GET', 'POST'])
def scan_file():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    if request.method == 'POST':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        # start_time = datetime.datetime.now()
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
        final_list,count_list=get_details(ingredient_list,mysql)
        # session['data'] = {
        #     "text": scanned_text,
        #     "time": str((datetime.datetime.now() - start_time).total_seconds())
        # }
        return render_template("result.html",result=final_list,data = count_list)

def show_products(id):

    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    get_products = "SELECT product,expiry,product_id FROM products where id = '%d'" % (id)
    cursor.execute(get_products)
    results = cursor.fetchall()
    
    # dic = {}
    # for name,exp,p_id in results:
    #     dic[p_id] = [name,exp]
    return results

@app.route('/dashboard',methods=['GET', 'POST'])
def dashboard():
    if session.get('userid'):
        dic = show_products(session.get('userid'))
        return render_template("profile.html",result=dic)
    else:
        return redirect('/new')
@app.route('/scan')
def scan():
    return render_template('scanner.html')

@app.route('/new_product',methods=['GET', 'POST'])
def add_product():
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method== "POST":
        prod_name=request.form['name']
        expiry_date=request.form['date']
        # add query to to insert into db
        print(type(expiry_date))
        # expiry_date = datetime.strftime(expiry_date,"%Y-%m-%d")
        print(expiry_date)
        cursor.execute("INSERT INTO products(product_id,id,product,expiry) VALUES (NULL,%s,%s,%s)" , (session.get("userid"),prod_name,expiry_date))
        # cursor.execute(prod_to_add)
        conn.commit()
        return redirect('/dashboard')
    else:
        return render_template("new_product.html")

@app.route('/edit_product/<string:p_id>',methods=['GET', 'POST'])
def edit_product(p_id):
    # id = session.get("userid")
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    prod_to_edit= "SELECT product,expiry from products where product_id = '%s'" % (p_id)
    cursor.execute(prod_to_edit)
    results = cursor.fetchone() 
    if request.method== 'POST':
        prod_name=request.form['name']
        expiry_date=request.form['date']
        
        prod_to_update = "UPDATE products SET product = '%s', expiry = '%s' where product_id = '%s'" % (prod_name,expiry_date,p_id)
        cursor.execute(prod_to_update)
        conn.commit()
        return redirect('/dashboard')   
    else: 
        return render_template("edit_product.html",result=results)

@app.route('/remove_product/<string:p_id>',methods=['POST'])
def remove_product(p_id):
    # Create cursor
    conn = mysql.connect()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # Execute
    delete = "DELETE FROM products WHERE product_id = '%s'" % (p_id)
    cursor.execute(delete)

    # Commit to DB
    conn.commit()
    # flash('Article Deleted', 'success')

    return redirect('/dashboard')

# @app.route('/remove_product')
# def remove_product():
#     id = session.get("userid")
#     conn = mysql.connect()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     prod_to_edit= "SELECT product,expiry,product_id from products where product_id = '%d'" % (id)
#     cursor.execute(prod_to_edit)

#     if request.method== 'POST':
#         prod_name=request.form['name']
#         expiry_date=request.form['date']
        
#         prod_to_update = "UPDATE products SET product = '%s', expiry = '%s' where product_id = '%s'" % (prod_name,expiry_date,id)
#         cursor.execute(prod_to_update)
#         conn.commit()
#         return redirect('/dashboard')   
#     else: 
#         return render_template("edit_product.html",result=prod_to_edit)



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
        cursor.execute('SELECT id,fullname FROM userdetails WHERE email = %s AND password = %s', (email, password))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            msg = "Sucessfully logged-In"
            # cursor.execute('SELECT ')
            user_id= account['id'] # sql query for getting uid from email 
            fullname = account['fullname']
            # print(account['id'])
            session['userid']=user_id
            session['fullname'] = fullname
            
            # return render_template("login.html",msg=msg)
            # time.sleep(2)
            # flash('Article Created', 'success')
            return redirect('/dashboard')

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)

    return render_template("login.html",msg=msg)

@app.route("/test_ajax")
def test_ajax():
    category= categories()
    return render_template("recommend.html",category=category)

# subset=pd.DataFrame()
@app.route("/getDataAjax",methods=['GET','POST'])
def getDataAjax():
    res=[]
    if request.method=='POST':
        # courses={
        #     'Cosmetic':['Peach 1','Peach 2','Peach 3','Peach 4'],
        #     'Sun':['Bhopla 1','Bhopla 2','Bhopla 3','Bhopla 4'],
        # }
        global category_type
        category_type= request.form['data']
        brand=brands(request.form['data'])
        global subset
        subset=brand[1]
        # res=courses[request.form['data']]
    return render_template("get_data.html",data=brand)

@app.route("/dropdown3",methods=['GET','POST'])
def dropdown3():
    res=[]
    if request.method=='POST':
        # courses={
        #     'Cosmetic':['Peach 1','Peach 2','Peach 3','Peach 4'],
        #     'Sun':['Bhopla 1','Bhopla 2','Bhopla 3','Bhopla 4'],
        # }
        print(subset)
        global prod_name
        #prod_name=request.form['data']
        prod=products(request.form['data'],subset)
        # res=courses[request.form['data']]
    return render_template("dropdown3.html",data=prod)

@app.route("/submit_button",methods=['GET','POST'])
def submit_button():
    print("INSIDE BTN")
    data_frame= recommend(category_type,request.form['data'])
    return render_template("answer.html", data=data_frame.to_dict(orient='records'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/new")

if __name__ == '__main__':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    app.run(debug=True)