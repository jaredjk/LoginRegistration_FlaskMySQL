from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import MySQLConnector
import re
import time
import md5 #need to import for hashed password md5 to work

app = Flask(__name__)
app.secret_key = 'ItsSecretKey'
mysql = MySQLConnector(app, 'mydb')

FIRSTLAST_REGEX = re.compile(r'^(?=.*[0-9]).+$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
UPPERDIGIT_REGEX = re.compile(r'^(?=.*[0-9])(?=.*[A-Z]).+$')

@app.route('/')
def index():
    session['loggedOn'] = False
    return render_template("index.html")

@app.route('/result', methods=['POST'])
def results():
    if request.form['action'] == 'signIn':
        email = request.form['email']
        password = request.form['password']
        hashed_password = md5.new(password).hexdigest()
        check = "SELECT * FROM logregist"
        for i in (mysql.query_db(check)):
            if i['email'] == email and i['password']: #== hashed_password:
                session['loggedOn'] = True
                flash("{} {}! Welcome!".format(i['first_name'], i['last_name']))
                return redirect('/')

        flash('incorrect email/password')
        return redirect('/')

@app.route('/success', methods=['POST'])
def return_route():
    # request.form['register'] == 'regi':
    # first_name = request.form['first_name']
    # last_name = request.form['last_name']
    # email = request.form['email']

    confirm_password = request.form['confirm_password']
    query = "INSERT INTO logregist (first_name, last_name, email, password) VALUES (:first_name, :last_name, :email, :password)"
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    hashed_password = md5.new(password).hexdigest()    
    data = {
            'first_name': first_name,
            'last_name': last_name,
            'email':  email,
            'password': hashed_password
            }

    

    mysql.query_db(query, data)
    if len(first_name) < 1:
        flash("First Name cannot be empty!")
        return redirect('/')

    elif FIRSTLAST_REGEX.match(first_name):
        flash("Invalid First Name")
        return redirect('/')

    elif len(last_name) < 1:
        flash("Last Name cannot be empty!")
        return redirect('/')

    elif FIRSTLAST_REGEX.match(last_name):
        flash("Invalid Last Name")
        return redirect('/')

    elif len(email) < 1:
        flash("Email cannot be empty!")
        return redirect('/')

    elif not EMAIL_REGEX.match(email):
        flash("Invalid Email")
        return redirect('/')   

    elif len(password) < 1:
        flash("Password cannot be empty!")
        return redirect('/')

    elif len(password) < 8:
        flash("Password must be longer than 8 characters!")
        return redirect('/')

    elif not UPPERDIGIT_REGEX.match(password):
        flash("Password must contain at least one upper case letter and one digit")
        return redirect('/')

    elif len(confirm_password) < 1:
        flash("Please confirm password")
        return redirect('/')

    elif password != confirm_password:
        flash("Password must match!")
        return redirect('/')
    else:
        return render_template('success.html')
app.run(debug=True)