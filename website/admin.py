from flask import Blueprint, render_template, request, session, flash, redirect, url_for
import sqlite3
admin = Blueprint("admin", __name__)

sqldbname = 'GUITAR.db'

@admin.route('/')
def index():
  conn = sqlite3.connect(sqldbname)
  cursor = conn.cursor()
  sqlcommand = ("SELECT * FROM GUITAR")
  cursor.execute(sqlcommand)
  storages = cursor.fetchall()
  conn.close()
  return render_template('admin/dashboard.html', storages=storages)

@admin.route('/add', methods=['GET','POST'])
def add():
  if request.method == 'POST':
    product = request.form['Product']
    brand = request.form['Brand']
    rating = request.form['Rating']
    model = request.form['Model']
    picture = request.form['Picture']
    price = request.form['Price']
    details = request.form['Details']
    
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO GUITAR (product, brand, rating, model, picture, price, details) VALUES(?,?,?,?,?,?,?)", (product, brand, rating, model, picture, price, details))
    conn.commit()
    conn.close()
    flash("You have added successfully", "success")
    return redirect(url_for('admin.index'))
  return render_template('admin/add.html')

@admin.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
  conn = sqlite3.connect(sqldbname)
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM GUITAR where id = ?", (id,))
  storage = cursor.fetchone()
  conn.close()
  if request.method == 'POST':
    product = request.form['Product']
    brand = request.form['Brand']
    rating = request.form['Rating']
    model = request.form['Model']
    picture = request.form['Picture']
    price = request.form['Price']
    details = request.form['Details']
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute("Update GUITAR set product = ?, brand = ?, rating = ?, model = ?, picture = ?, price = ?, details = ? where id = ?", (product, brand, rating, model, picture, price, details, id))
    conn.commit()
    conn.close()
    flash("Product updated successfully!", "success")
    return redirect(url_for("admin.index"))
  return render_template("admin/edit.html", storage=storage)



@admin.route('/delete/<int:id>', methods=['POST'])
def delete(id):
  conn = sqlite3.connect(sqldbname)
  cursor = conn.cursor()
  cursor.execute("DELETE FROM GUITAR WHERE id = ?", (id,))
  conn.commit()
  conn.close()
  flash("You have successfully deleted the item", "success")
  return redirect(url_for('admin.index'))
