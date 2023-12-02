import json
import os

from flask import Flask, render_template, redirect, url_for, flash, abort, request, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = Paid_user.query.get(int(user_id))
    if user:
        return user
    # If not, check if user is in free_user table

    # If user is not in either table, return None


app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
with app.app_context():
    class Paid_user(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))


    class Orders(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True)
        email = db.Column(db.String(100))
        people = db.Column(db.Integer)
        special = db.Column(db.String(100))


    class Breakfast(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True)
        description = db.Column(db.String(1000))
        link = db.Column(db.String(1000))
        price = db.Column(db.String(100))


    class Lunch(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True)
        description = db.Column(db.String(1000))
        link = db.Column(db.String(1000))
        price = db.Column(db.String(100))


    class Diner(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), unique=True)
        description = db.Column(db.String(1000))
        link = db.Column(db.String(1000))
        price = db.Column(db.String(100))


    db.create_all()


class MyModelView(ModelView):
    def is_accessible(self):
        return True


admin = Admin(app)
admin.add_view(MyModelView(Paid_user, db.session))
admin.add_view(MyModelView(Orders, db.session))
admin.add_view(MyModelView(Breakfast, db.session))
admin.add_view(MyModelView(Lunch, db.session))
admin.add_view(MyModelView(Diner, db.session))


@app.route("/")
def start():
    return render_template("index.html", message_1="Enjoy", message_2="Your Meal")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        phone=request.form.get("phone")
        password=request.form.get("password")
        user=Paid_user.query.filter_by(phone=phone).first()
        if phone==user.phone and password ==user.password:
            login_user(user)
            return redirect("/add")
    return render_template("login.html")


@app.route("/book", methods=["GET", "POST"])
def book():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        date = request.form.get("date")
        people = request.form.get("people")
        special = request.form.get("request")
        new_order = Orders(
            name=name, email=email, people=people, special=special
        )
        db.session.add(new_order)
        db.session.commit()
        return render_template("index.html", message_1="Your order ", message_2="is registered ")
    return render_template("booking.html")


@app.route('/control', methods=["GET", "POST"])
def controle():
    orders = Orders.query.all()

    return render_template("service.html", orders=orders)

@login_required
@app.route("/delete/<name>")
def delete(name):
    deleted_order = Orders.query.filter_by(name=name).first()
    if deleted_order:
        db.session.delete(deleted_order)
        db.session.commit()
        return redirect("/control")
    else:

        return "somthing went wrong "

@login_required
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":
        name = request.form.get("name")
        target = request.form.get("choice")
        description = request.form.get("description")
        link = request.form.get("link")
        price = request.form.get("price")
        if target == "breakfast":
            new_breakfast = Breakfast(
                name=name,
                description=description,
                link=link,
                price=price
            )
            db.session.add(new_breakfast)
            db.session.commit()
        elif target == "lunch":
            new_lunch = Lunch(
                name=name,
                description=description,
                link=link,
                price=price
            )
            db.session.add(new_lunch)
            db.session.commit()
        elif target == "diner":
            new_diner = Diner(
                name=name,
                description=description,
                link=link,
                price=price
            )
            db.session.add(new_diner)
            db.session.commit()
            return redirect("/menue")
    return render_template("addfood.html")


@app.route("/menue")
def menue():
    all_breakfast = Breakfast.query.all()
    all_lunch = Lunch.query.all()
    all_diner = Diner.query.all()
    return render_template("menu.html", all_breakfast=all_breakfast, all_lunch=all_lunch, all_diner=all_diner,current_user=current_user)

@app.route("/adminmenue")
@login_required
def adminmenue():
    all_breakfast = Breakfast.query.all()
    all_lunch = Lunch.query.all()
    all_diner = Diner.query.all()
    return render_template("adminmenue.html", all_breakfast=all_breakfast, all_lunch=all_lunch, all_diner=all_diner,current_user=current_user)


@app.route('/delete-food', methods=['GET', 'POST'])
def delete_food():
    food_name = request.form['food-name']
    deleted_food = add.query.filter_by(name=add).first()
    if deleted_food:
        db.session.delete(deleted_food)
        db.session.commit()
    return redirect("/menue")
# Route to delete a breakfast item
@app.route('/delet_breakfast', methods=['GET'])
@login_required
def delete_breakfast():
    # Get the 'food' parameter from the URL
    food_id = request.args.get('food')
    target=Breakfast.query.filter_by(id=food_id).first()
    db.session.delete(target)
    db.session.commit()
    return redirect("/adminmenue")
@app.route("/logout")
def logout():
    login_user(current_user)
    return "loged out "
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
