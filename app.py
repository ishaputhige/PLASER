from flask import Flask, request, render_template, redirect, url_for, session

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/s')
def price():
    return render_template("scanner.html")

if __name__ == '__main__':
    app.run(debug=True)