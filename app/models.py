from app import db, bcrypt
from datetime import datetime, timedelta
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.String(4), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    identification_code = db.Column(db.String(10), unique=True, nullable=False)  # РНОКПП
    password = db.Column(db.String(100), nullable=False)
    accounts = db.relationship('Account', backref='user', lazy=True)
    loans = db.relationship('Loan', backref='user', lazy=True)
    cards = db.relationship('Card', backref='user', lazy=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Float, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_number = db.Column(db.String(16), unique=True, nullable=False)
    cvv = db.Column(db.String(3), nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # deposit, withdrawal, transfer
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # ID отримувача для переказів
    recipient = db.relationship('User', foreign_keys=[recipient_id])  # зв'язок з отримувачем

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    term_months = db.Column(db.Integer, nullable=False)
    remaining_balance = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Deposit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    term = db.Column(db.Integer, nullable=False)  # термін у місяцях
    interest_rate = db.Column(db.Float, nullable=False)  # відсоткова ставка
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    interest = db.Column(db.Float, nullable=False)  # сума відсотків
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, amount, term, interest_rate, user_id):
        self.amount = amount
        self.term = term
        self.interest_rate = interest_rate
        self.user_id = user_id
        self.start_date = datetime.utcnow()
        self.end_date = self.start_date + timedelta(days=30 * term)
        self.interest = amount * interest_rate * term / 12  # розрахунок відсотків

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    image_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<News {self.title}>'