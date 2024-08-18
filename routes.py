from flask import render_template, redirect, url_for, request
from app import rupiah_format 
from app import app, db, login_manager
from models import User, MenuItem, Purchase, Order, OrderItem
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Redirect based on user role
            if user.is_admin:
                return redirect(url_for('admin'))
            return redirect(url_for('menu'))
        return 'Invalid username or password'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        # Cek apakah username sudah ada
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists. Please choose a different username.', 400
        
        # Jika tidak, buat user baru
        new_user = User(username=username, password=hashed_password)  # Gunakan 'password' di sini
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/menu', methods=['GET', 'POST'])
@login_required
def menu():
    message = None
    receipt_url = None

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity = int(request.form.get('quantity'))
        confirm = request.form.get('confirm')

        item = MenuItem.query.get(item_id)
        if item:
            total_price = item.price * quantity
            formatted_price = rupiah_format(total_price, with_prefix=True)

            if confirm == 'no':
                # Kembali ke menu jika pengguna tidak yakin
                return redirect(url_for('menu'))
            elif confirm == 'yes':
                # Simpan order dan order items
                order = Order(user_id=current_user.id, total_amount=total_price)
                db.session.add(order)
                db.session.commit()

                order_item = OrderItem(order_id=order.id, menu_item_id=item.id, quantity=quantity, price=item.price)
                db.session.add(order_item)
                db.session.commit()

                receipt_url = url_for('receipt', order_id=order.id)
                message = f"Order confirmed: {quantity} of {item.name}. Total price: {formatted_price}. Click 'Print Receipt' to generate PDF."
        else:
            message = "Item not found."

    items = MenuItem.query.all()
    return render_template('menu.html', items=items, message=message, receipt_url=receipt_url)


@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    item_id = request.form.get('item_id')
    quantity = request.form.get('quantity')
    item = MenuItem.query.get(item_id)
    if item:
        new_purchase = Purchase(item_id=item.id, quantity=quantity)
        db.session.add(new_purchase)
        db.session.commit()
        return redirect(url_for('receipt', purchase_id=new_purchase.id))
    return 'Item not found', 404

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    message = None

    if request.method == 'POST':
        if 'create' in request.form:
            name = request.form.get('name')
            price = request.form.get('price')
            new_item = MenuItem(name=name, price=price)
            db.session.add(new_item)
            db.session.commit()
            message = 'Menu item created successfully!'
            return render_template('admin.html', items=MenuItem.query.all(), message=message)

        elif 'update' in request.form:
            item_id = request.form.get('item_id')
            name = request.form.get('name')
            price = request.form.get('price')
            item = MenuItem.query.get(item_id)
            if item:
                item.name = name if name else item.name
                item.price = float(price) if price else item.price
                db.session.commit()
                message = 'Menu item updated successfully!'
            else:
                message = 'Item not found.'
            return render_template('admin.html', items=MenuItem.query.all(), message=message)

        elif 'delete' in request.form:
            item_id = request.form.get('item_id')
            item = MenuItem.query.get(item_id)
            if item:
                db.session.delete(item)
                db.session.commit()
                message = 'Menu item deleted successfully!'
            else:
                message = 'Item not found.'
            return render_template('admin.html', items=MenuItem.query.all(), message=message)

    # Get request or after POST operation completion
    return render_template('admin.html', items=MenuItem.query.all(), message=message)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/receipt/<int:order_id>', methods=['GET'])
@login_required
def receipt(order_id):
    order = Order.query.get(order_id)
    if not order or order.user_id != current_user.id:
        return redirect(url_for('menu'))

    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('receipt.html', order=order, order_items=order_items)

@app.route('/admin/orders', methods=['GET'])
@login_required
def admin_orders():
    if not current_user.is_admin:
        return redirect(url_for('index'))

    orders = Order.query.all()
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/order/<int:order_id>', methods=['GET'])
@login_required
def admin_order_details(order_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))

    order = Order.query.get(order_id)
    if not order:
        return 'Order not found', 404

    order_items = OrderItem.query.filter_by(order_id=order.id).all()

    return render_template('admin_order_details.html', order=order, order_items=order_items)



