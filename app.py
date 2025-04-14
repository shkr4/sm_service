from flask import Flask, render_template, request, jsonify, url_for, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
# from flask_admin.contrib.sqla import ModelView
from flask_mail import Mail, Message
from dotenv import load_dotenv
import os
from datetime import datetime
from myFunctions import *
from adminClass import *
import pytz

IST = pytz.timezone('Asia/Kolkata')

load_dotenv()


mailPort = int(os.environ.get('port'))
mailServer = os.environ.get('server')
mailUsername = os.environ.get('sender_email')
mailPassword = os.environ.get('mailpasswd')

app = Flask(__name__)

app.config['MAIL_SERVER'] = mailServer
app.config['MAIL_PORT'] = mailPort
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = mailUsername
app.config['MAIL_PASSWORD'] = mailPassword
app.config['MAIL_DEFAULT_SENDER'] = mailUsername
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = "secretkey"

db = SQLAlchemy(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = "dashboard"
admin = Admin(app, name="My Admin Panel",
              template_mode="bootstrap4", url='/super-admin')


class Admins(db.Model, UserMixin):
    __tablename__ = "admins"

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def get_id(self):
        return str(self.ID)

    def check_password(self, password):
        return self.password == password  # Replace with hashing in production

    @staticmethod
    def get_by_username(username):
        return Admins.query.filter_by(username=username).first()


class Customers(db.Model):
    __tablename__ = 'customer'

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(240), nullable=False)
    ph = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    payments = db.relationship('Payment', backref="customer")

    def __str__(self):
        return f"{self.name} ({self.ph})"


class Payment(db.Model):
    __tablename__ = 'payment'
    ID = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.ID'))
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default="live")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST))


with app.app_context():
    db.create_all()

admin.add_view(adminsAdmin(Admins, db.session))
admin.add_view(customersAdmin(Customers, db.session))
admin.add_view(paymentAdmin(Payment, db.session))


@login_manager.user_loader
def load_user(user_id):
    return Admins.query.get(int(user_id))


@app.route('/home')
@login_required
def home():
    return render_template('admin.html', user=current_user)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = Admins.get_by_username(username)
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            return ("Invalid username or password")
    else:
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/check-mobile')
@login_required
def check_mobile():
    number = request.args.get('number')
    customer = Customers.query.filter_by(ph=number).first()
    if customer:
        name = session["name"] = customer.name
        email = session["email"] = customer.email
        address = session["address"] = customer.address
        return jsonify({"name": name, "email": email, "address": address}), 200
    else:
        return jsonify({"msg": "Customer not found"}), 400


@app.post('/submitData')
@login_required
def submitData():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    amount = data.get('amount')
    address = data.get('address')
    comment = data.get('comment')
    mobile = data.get('mobile')

    customer = Customers.query.filter_by(ph=mobile).first()

    if not customer:
        newCustomer = Customers(
            name=name, email=email, address=address, ph=mobile)
        db.session.add(newCustomer)
        db.session.flush()
        newPayment = Payment(customer_id=newCustomer.ID,
                             amount=amount, comment=comment)
        db.session.add(newPayment)
        print(newPayment)
        return addEnteryAndSendEmail(db, jsonify, name, email, amount, mail, Message)

    else:

        if name != session.get("name"):
            customer.name = name
        if email != session.get("email"):
            customer.email = email
        if address != session.get("address"):
            customer.address = address
        newPayment = Payment(customer_id=customer.ID,
                             amount=amount, comment=comment)
        db.session.add(newPayment)

        return addEnteryAndSendEmail(db, jsonify, name, email, amount, mail, Message)


@app.get('/customer/<mobnum>')
def customerViewPoint(mobnum):
    customer = Customers.query.filter_by(ph=mobnum).first()
    payment = Payment.query.filter_by(customer_id=customer.ID).all()
    return render_template('customerPage.html', customer=customer, payment=payment)
