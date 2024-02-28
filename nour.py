from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

app = Flask(__name__)
babel = Babel(app)

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    # Check if user is in paid_user table
    user = User.query.get(int(user_id))
    if user:
        return user
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nour.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'fr', 'es']

db = SQLAlchemy(app)
with app.app_context():
    class User(UserMixin, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        phone = db.Column(db.String(100), unique=True)
        password = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        email = db.Column(db.String(100))
    class chairs( db.Model):
        id = db.Column(db.Integer, primary_key=True)

        pricew = db.Column(db.String(100))
        name = db.Column(db.String(1000))
        photo = db.Column(db.String(10000))
    db.create_all()
class MyModelView(ModelView):
    def is_accessible(self):
        return True


admin = Admin(app)
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(chairs, db.session))
@app.route('/')
def index():
    all_chairs=chairs.query.all()
    return render_template('index.html',all_chairs=all_chairs)


@app.route("/register" , methods = ["GET", "POST"])
def register():
    name= request.get.form("name")
    password= request.get.form("password")
    phone= request.get.form("phone")
    email= request.get.form("email")
    new_user = User(

    name=name, password=password, email=email,phone=phone


    )
    db.session.add(new_user)
    db.session.commit()
    return render_template("registration.html")

@app.route("/login",methods=["GET","POST"])
def login ():
    if request.method=="POST":
        phone=request.form.get("phone")
        password=request.form.get("password")
        user=User.query.filter_by(phone=phone).first()
        if user and user.password==password:
            login_user(user)
            return redirect("/dash")
        else:
            return "wrong crediential"
    return render_template("login.html")


@app.route("/logout")
def dash():
    logout_user()
    return "done"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)