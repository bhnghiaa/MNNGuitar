from flask import Blueprint, render_template, session, request, redirect, url_for, flash
import sqlite3
auth = Blueprint("auth", __name__)

sqldbname = 'GUITAR.db'

def SaveToDB(name,email,password):
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    sqlcommand = "SELECT Max(user_id) from user"
    cur.execute(sqlcommand)
    id_max = cur.fetchone()[0]
    id_max = id_max + 1
    cur.execute("INSERT INTO user (user_id, name, email, password, admin) VALUES (?,?,?,?,?)",(id_max,name,email,password,0))
    conn.commit()
    conn.close()
    return id_max

def get_obj_user(username,password):
    result =[]
    conn = sqlite3.connect(sqldbname)
    cur = conn.cursor()
    sqlcommand = "Select * from user where name =? and password = ?"
    cur.execute(sqlcommand,(username,password))
    obj_user = cur.fetchone()
    if obj_user:
        result = obj_user
    conn.close()
    return result;


@auth.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['txt_username']
        password = request.form['txt_password']
        obj_user = get_obj_user(username,password)
        if obj_user:
          obj_user ={
                "id" : obj_user[0],
                "name": obj_user[1],
                "email":obj_user[2],
                "admin": obj_user[4]
          }
          if obj_user["admin"] == 0:
            session['current_user'] = obj_user
            flash("You have log in successfully", "success")
            return redirect(url_for('views.account'))
          elif obj_user["admin"] == 1:
           session['current_user'] = obj_user
           flash("You have log in successfully as admin of page", "success")
           return redirect(url_for('admin.index'))        
        flash("Please check your username and password", 'error')
        return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route("/signup", methods=['GET','POST'])
def sign_up():
  if request.method == 'POST':
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    username_error = ""
    email_error = ""
    password_error = ""
    if not username:
      username_error = "Username is required."
    if not password: 
      password_error = "Password is required."
    if not email: 
      email_error = "Email is required."
    if username_error or password_error or email_error:
      return render_template("signup.html", username_error = username_error, password_error =password_error, email_error =email_error, registeration_success = "")
    newid = SaveToDB(username, email, password)
    flash("You have sign up successfully", "success")
    return redirect(url_for("auth.login"))
    # stroutput = f'Registered: Username: {username},Email: {email}, Password: {password}'
    # registeration_success = "Registeration successful with id = "+ str(newid)
    
  return render_template("signup.html")
  

@auth.route("/logout")
def logout():
    session.pop('current_user', None)
    session.pop('cart', None)
    return redirect(url_for('views.home'))