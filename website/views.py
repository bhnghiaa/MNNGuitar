from flask import Blueprint, render_template, request, session, flash, redirect, url_for
import sqlite3
views = Blueprint("views", __name__)


sqldbname = 'GUITAR.db'
@views.context_processor
def my_utility_processor():
    def convert_currency_to_int(currency_str):
        currency_str = currency_str.replace("$", "").replace(".", "")
        return int(currency_str)
    def convert_int_to_currency(number):
        number_str = str(number)
        currency_str = ""
        count = 0

        for digit in reversed(number_str):
            if count != 0 and count % 3 == 0:
                currency_str = "." + currency_str
            currency_str = digit + currency_str
            count += 1

        currency_str = "$" + currency_str
        return currency_str
    return dict(convert_currency_to_int=convert_currency_to_int, convert_int_to_currency=convert_int_to_currency)

@views.route('/')
def home():
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM GUITAR LIMIT 0, 4'
    cursor.execute(sqlcommand)
    featuresProduct = cursor.fetchall()
    sqlcommand = 'SELECT * FROM GUITAR LIMIT 4, 10'
    cursor.execute(sqlcommand)
    latestProducts = cursor.fetchall()
    return render_template('home.html', featuresProduct=featuresProduct, latestProducts=latestProducts,user_name = current_username)

@views.route('/cart', methods=['GET'])
def shopping_cart():
    current_username = ""
    current_cart = []
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    if 'cart' in session:
        current_cart = session.get('cart', [])

    return render_template('cart.html', cart=current_cart,user_name = current_username)

@views.route('/all_products')
def all_products():
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM GUITAR'
    cursor.execute(sqlcommand)
    all_products = cursor.fetchall()
    return render_template('all_products.html', all_products=all_products,user_name = current_username)

@views.route('/product_detail/<id>')
def product_detail(id):
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    sqlcommand = 'SELECT * FROM GUITAR WHERE id = ?'
    cursor.execute(sqlcommand, (id,))
    product_detail = cursor.fetchone()
    sqlcommand = 'SELECT * FROM GUITAR LIMIT 0, 4'
    cursor.execute(sqlcommand)
    related_products = cursor.fetchall()
    return render_template('product_detail.html', product_detail=product_detail, related_products=related_products, user_name = current_username)

@views.route('/about')
def about():
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    return render_template('about.html' ,user_name = current_username)


@views.route('/contact', methods=['GET', 'POST'])
def contact():
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    if request.method == 'POST':
        Name = request.form['Name']
        Tel = request.form['Tel']
        Email = request.form['Email']
        Message = request.form['message']
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Contact (Name, Tel, Email, Messages) VALUES(?,?,?,?)", (Name, Tel, Email, Message))
        conn.commit()
        conn.close()
        flash("Thank you for your feedback", "success")
        return redirect(url_for('views.contact'))
    return render_template('contact.html',user_name = current_username)

@views.route('/cart/add', methods=['POST'])
def addToCart():
    productId = request.form['product_id']
    quantity = int(request.form['quantity'])
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT product, price, picture FROM GUITAR WHERE id = ?", (productId,))
    product = cursor.fetchone()
    conn.close()
    product_detail = {
        "id": productId,
        "name": product[0],
        "price": product[1],
        "image": product[2],
        "quantity": quantity
    }
    cart = session.get('cart', [])
    found = False
    for item in cart:
        if item["id"] == productId:
            item["quantity"] += quantity
            found = True
            break
    if not found:
        cart.append(product_detail)
    session["cart"] = cart
    flash('Item added successfully!', 'success')
    return redirect(url_for('views.product_detail', id=productId))

@views.route('/cart/update',methods = ['POST'])
def CartUpdate():
    cart = session.get('cart', [])
    new_cart = []
    for row in cart:
        productId = int(row['id'])
        if f'quantity-{productId}' in request.form:
            quantity = int(request.form[f'quantity-{productId}'])
            if quantity == 0 or f'delete-{productId}' in request.form:
                continue
            row['quantity'] = quantity
        new_cart.append(row)
    session['cart'] = new_cart
    return redirect(url_for('views.shopping_cart'))

@views.route('/proceed_cart',methods = ['POST'] )
def proceed_cart():
    if 'current_user' in session:
        user_id = session['current_user']['id']
        user_email = session['current_user']['email']
        if 'cart' in session:
            current_cart = session.get("cart",[])
            if current_cart is not []:
                conn = sqlite3.connect(sqldbname)
                cur = conn.cursor()
                status = 1
                cur.execute('INSERT INTO "order" (user_id, user_email,status) VALUES(?, ?, ?)',(user_id,user_email,status))
                order_id = cur.lastrowid
                for product in current_cart:
                    product_id = product['id']
                    price = product['price']
                    quantity = product['quantity']
                    cur.execute('INSERT or REPLACE INTO "order_details" (order_id, product_id, price, quantity) VALUES(?,?,?,?)',(order_id,product_id,price,quantity))  
                conn.commit()
                conn.close()
                if 'cart' in session:
                    current_cart = session.pop("cart",[])
                flash(f'Your order has been successfully created: orderID: {order_id}')
                return redirect(url_for("views.account"))  
        flash("There is nothing in cart. Let's add some!", "info")
        return redirect(url_for("views.all_products"))
    flash("You are not logged in. Please login", "error")
    return redirect(url_for("auth.login"))
    

@views.route('/account/',methods = ['GET'])
def account():
    user_orders = []
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    user_id = session.get('current_user',{}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cur = conn.cursor()
        cur.execute('Select * from "order" where user_id = ?',(user_id,))
        user_orders = cur.fetchall()
        conn.close()
        return render_template('account.html',orders = user_orders, user_name = current_username)
    flash("User not logged in")
    return redirect(url_for("auth.login"))

@views.route('/order/', defaults={'order_id':None}, methods = ['GET'])
@views.route('/order/<int:order_id>/', methods = ['GET'])
def order(order_id):
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    user_id = session.get('current_user',{}).get('id')
    if user_id:
        conn = sqlite3.connect(sqldbname)
        cur = conn.cursor()
        if order_id is not None:
            cur.execute('Select * from "order" where id = ? and user_id = ?',(order_id,user_id))
            order = cur.fetchone()
            cur.execute('SELECT * from order_details where order_id = ?',(order_id,))
            order_details = cur.fetchall()
            conn.close()
            return render_template('orders.html',order = order,order_details = order_details, user_name = current_username)
        else:
            cur.execute('Select * from "order" where user_id = ?',(user_id,))
            user_orders = cur.fetchall()
            if not user_orders:
                user_orders = None
            conn.close()
            return render_template('account.html',orders = user_orders, user_name = current_username)
    flash("User not logged in")
    return redirect(url_for("auth.login"))

@views.route("/sort-form", methods=["POST"])
def process_sort_form():
    selected_option = request.form.get('sort-dropdown')
    conn = sqlite3.connect(sqldbname)
    cursor = conn.cursor()
    match selected_option:
        case "Default Sort":
            sqlcommand = ("select * from GUITAR")
        case "Sort By Price":
            sqlcommand = ("select * from GUITAR ORDER BY CAST(REPLACE(REPLACE(price, '$', ''), '.', '') AS INT)")
        case "Sort By Price DESC":
            sqlcommand = ("select * from GUITAR ORDER BY CAST(REPLACE(REPLACE(price, '$', ''), '.', '') AS INT) DESC")
        case "Sort By Rating":
            sqlcommand = ("select * from GUITAR ORDER BY rating DESC")
        case "Sort By Brand":        
            sqlcommand = ("select * from GUITAR ORDER BY brand")
    cursor.execute(sqlcommand)
    data = cursor.fetchall()
    conn.close()
    return render_template('all_products.html', all_products=data)

@views.route('/search', methods=['POST'])
def search():
    current_username = ""
    if 'current_user' in session:
        current_username = session['current_user']['name']
    else:
        current_username = ""
    search_text = request.form['searchInput']
    if search_text == "":
        flash("You must add some text", "error")
    if search_text != None:
        flash(search_text, 'success')
        conn = sqlite3.connect(sqldbname)
        cursor = conn.cursor()
        sqlcommand = (
            "select * from GUITAR where product like '%") + search_text + "%'"
        cursor.execute(sqlcommand)
        data = cursor.fetchall()
        conn.close()
    return render_template('all_products.html', search_text=search_text, all_products=data, user_name = current_username)