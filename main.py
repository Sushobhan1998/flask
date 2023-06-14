from flask import Flask, render_template, request, redirect, session
import mysql.connector
import  os
import bcrypt, re
from config import *

app=Flask(__name__)
app.secret_key = os.urandom(25)


try :
    conn = mysql.connector.connect(
        user = customUser,
        password = customPassword,
        host = customHostname,
        database=customDb
    )
    cursor = conn.cursor()
except Exception as ex :
    print("Can't connect to database !!",ex)

@app.route("/signUp", methods=['POST', 'GET'])
def signUp() :
    email = request.form.get('email')
    password = request.form.get('password')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    cursor.execute("INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)", (email, hashed_password))
    conn.commit()
    return "Registered succesfully!!!!"

@app.route("/")
def signIn() :

    return render_template("signIn.html")


@app.route("/login-validation", methods=['POST'])
def login_validation() :
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM `users` WHERE `email` LIKE %s""", (email,))
    existUsers = cursor.fetchall()
    
    if len(existUsers) > 0 :
        stored_password = existUsers[0][2]
        if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
            session['email'] = existUsers[0][1]
            print(existUsers)
            
            # Split the email into local part and domain part
            local_part, domain_part = email.split('@')

            # Extract the name from the local part using regular expressions
            name = re.sub(r'[^\w\s]', '', local_part).strip()

            name = name.capitalize()
        
            return render_template('dashboard.html', email=name, password=password)
    
    return render_template("/signIn.html", invalid = "Invalid credentials!!!")


@app.route("/dashBoard")
def dashBoard() :
    if 'email' in session :
        return render_template("dashBoard.html")
    else :
        return redirect("/")

@app.route("/logout")
def logout() :
    session.pop('email')
    return redirect("/")

if __name__ == "__main__" :
    app.run(host='0.0.0.0', port=80, debug=True)
