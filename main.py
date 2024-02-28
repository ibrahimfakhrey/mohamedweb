import json
import os
from sqlalchemy.orm import joinedload
from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = User.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None


app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    class Cart (db.Model):
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
        quantity = db.Column(db.Integer, default=1)


    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))


    class Product(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100))
        price = db.Column(db.Float)
        image_link = db.Column(db.String(255))






    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
        return True


admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Product, db.session))
admin.add_view(MyModelView(Cart, db.session))



@app.route("/")
def start():
    all_products=Product.query.all()
    return render_template("index.html",all_products=all_products)
@app.route("/register",methods=["GET","POST"])
def register():
    if request .method=="POST":
        new_user=User(
            phone=request.form.get("phone"),
            name=request.form.get("name"),
            email=request.form.get("email"),
            password= generate_password_hash(
            request.form.get('password'),
            method='pbkdf2:sha256',
            salt_length=8
        )
        )
        db.session.add(new_user)
        db.session.commit()
        sender_email = 'ibrahimfakhreyams@gmail.com'  # Your Gmail address
        app_password = 'qszc jcyr amyi vckn'  # The app password generated in step 2

        subject = 'confirmation from mohamed shop'
        body = 'لقد تلقينا طلبكم في التسجيل في موقعنا محمد شوب  مبروك كسبت معانا عربية   علشان ابنك محمد شاطر    '

        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = request.form.get("email")
        message['Subject'] = subject

        # Attach the body to the email
        message.attach(MIMEText(body, 'plain'))

        # Connect to Google's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            # Log in using your Gmail credentials
            server.login(sender_email, app_password)
            # Send the email
            server.sendmail(sender_email, request.form.get("email"), message.as_string())

        return 'Email sent successfully!'
    return render_template("register.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":

        password=  request.form.get('password')

        phone=request.form.get("phone")
        user = User.query.filter_by(phone=phone).first()
        if not user:
            flash("That email does not exist, please try again.")

            # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')

        # Email exists and password correct
        else:
            login_user(user)


            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    login_user(current_user)
    return "loged out "

@app.route("/add_product",methods=["GET","POST"])
def add_product():
    if request.method=="POST":
        name=request.form.get("name")
        price=request.form.get("price")
        image=request.form.get("image")
        new_product=Product(
            name=name,price=price,image_link=image
        )
        db.session.add(new_product)
        db.session.commit()
        return "product added successfuly"
    return render_template("add_product.html")


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # Check if the product exists
    product = Product.query.get_or_404(product_id)

    # Check if the product is already in the cart
    cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

    if cart_item:
        cart_item.quantity += 1
    else:
        cart_item = Cart(user_id=current_user.id, product_id=product_id)

    db.session.add(cart_item)
    db.session.commit()

    return redirect(url_for('cart'))
@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    cart_item = Cart.query.get_or_404(cart_id)

    if cart_item.user_id != current_user.id:
        abort(403)  # Forbidden

    db.session.delete(cart_item)
    db.session.commit()

    return redirect(url_for('cart'))
@app.route('/cart')
def cart():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(user_id=current_user.id).all()

    products = Product.query.all()  # Fetch all products

    return render_template('cart.html', cart_items=cart_items,products=products)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)