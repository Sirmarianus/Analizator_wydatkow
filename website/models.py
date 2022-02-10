from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    expenses = db.relationship('Expense')
    wallets = db.relationship('Wallet')


class Expenses_category(db.Model):
    __tablename__ = 'expenses_category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('expenses_category.id'), nullable=True)
    expenses = db.relationship('Expense')


class Wallet(db.Model):
    __tablename__ = 'wallet'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    ammount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(30), nullable=False)
    expenses = db.relationship('Expense')


class Expense(db.Model):
    __tablename__ = 'expense'
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallet.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expenses_category.id'), nullable=False)
    transaction_datetime = db.Column(db.DateTime, nullable=False)
    ammount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)