from flask import Blueprint, render_template, flash, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .data import data


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        email = data.instance().sql_injection_replace(email)
        if email != '' and password != '':
            cursor = db.cursor()
            cursor.execute("""SELECT * FROM users WHERE email = "{}" LIMIT 1; """.format(email))
            row = cursor.fetchone()
            if row is not None:
                if check_password_hash(password=password, pwhash=row[2]):
                    data.instance().login(row[0], row[1])
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect password, try again.', category='error')
            else:
                flash('Email does not exist.', category='error')
        else:
            flash("smth wrong with email", category='error')

    return render_template("login.html")


@auth.route('/logout')
def logout():
    data.instance().logout()
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":
        email = request.form.get('email')
        pass1 = request.form.get('password')
        pass2 = request.form.get('password_retype')
        
        email = data.instance().sql_injection_replace(email)

        if email != '' and pass1 != '' and pass2 != '':
            cursor = db.cursor()
            cursor.execute("""SELECT * FROM users WHERE email = "{}" LIMIT 1; """.format(email))
            row = cursor.fetchone()
            if row is not None:
                flash("Email already exists")
            elif pass1 != pass2:
                flash("Passwords don\'t match", category='error')
            else:
                password = generate_password_hash(pass1, method='sha256')
                cursor.execute("""INSERT INTO users(email, password) VALUES("{}", "{}");""".format(email, password))
                db.commit()
                flash('Account created!', category='success')
        else:
            flash("Fill up all forms", category='error')

    return render_template("signup.html")


@auth.route('/delete-expense', methods=['GET', 'POST'])
def delete_expense():
    if data.instance().is_logged():
        expense_id = request.args.get('expense_id')
        if expense_id.isdecimal():
            user_id = data.instance()._id
            cursor = db.cursor()
            cursor.execute("""SELECT user_id, amount, wallet_id FROM expenses WHERE id={}""".format(expense_id))
            _fetched_data = cursor.fetchone()
            if user_id == _fetched_data[0]:
                cursor.execute("""DELETE FROM expenses WHERE id={}""".format(expense_id))
                cursor.execute("""UPDATE wallets SET amount=amount+{} WHERE id={}""".format(_fetched_data[1], int(_fetched_data[2])))
                db.commit()

    return redirect(url_for('views.home'))


@auth.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    if data.instance().is_logged():
        if request.method == "POST":
            password = request.form.get('password')
            password_new = request.form.get('password-new')
            password_retype = request.form.get('password-retype')


            if password != '' and password_new != '' and password_retype != '':
                if password_new != password_retype:
                    flash("Passwords not the same")
                else:
                    cursor = db.cursor()
                    cursor.execute("""SELECT password FROM users WHERE id={}""".format(data.instance()._id))
                    password_hash = cursor.fetchone()[0]
                    if check_password_hash(password_hash, password):
                        cursor.execute("""UPDATE users SET password='{}' WHERE id={};""".format(generate_password_hash(password_new, method='sha256'), data.instance()._id))

            return redirect(url_for('views.settings'))
    else:
        return redirect(url_for('auth.login'))


@auth.route('/new-wallet', methods=['GET', 'POST'])
def new_wallet():
    _data = data.instance()
    if _data.is_logged():
        if request.method == "POST":
            name = request.form.get('name')
            name = _data.sql_injection_replace(name)
            currency = request.form.get('currency')
            currency = _data.sql_injection_replace(currency)
            amount = request.form.get('amount')
            amount = _data.sql_injection_replace(amount)

            if name != '' and currency != '' and amount != '' and amount.isdecimal():
                cursor = db.cursor()
                cursor.execute("""INSERT INTO wallets (name, user_id, amount, currency) VALUES ('{}', {}, {}, '{}')""".format(name, _data._id, amount, currency))
                db.commit()

            return redirect(url_for('views.settings'))

    else:
        return redirect(url_for('auth.login'))


@auth.route('/new-category', methods=['GET', 'POST'])
def new_category():
    _data = data.instance()
    if _data.is_logged():
        if request.method == "POST":
            new_category = request.form.get('new-category')
            new_category = _data.sql_injection_replace(new_category)

            if new_category != '':
                cursor = db.cursor()
                cursor.execute("""INSERT INTO expense_categories (user_id, name, parent_id) VALUES ({}, '{}', NULL)""".format(_data._id, new_category))
                db.commit()

            return redirect(url_for('views.settings'))

    else:
        return redirect(url_for('auth.login'))


@auth.route('/new-subcategory', methods=['GET', 'POST'])
def new_subcategory():
    _data = data.instance()
    if _data.is_logged():
        if request.method == "POST":
            new_subcategory = request.form.get('new-subcategory')
            new_subcategory = _data.sql_injection_replace(new_subcategory)

            category = request.form.get('category')

            if new_subcategory != '' and category.isdecimal():
                cursor = db.cursor()
                cursor.execute("""INSERT INTO expense_categories (user_id, name, parent_id) VALUES ({}, '{}', {}})""".format(_data._id, new_subcategory, category))
                db.commit()

            return redirect(url_for('views.settings'))

    else:
        return redirect(url_for('auth.login'))


@auth.route('/delete-wallet', methods=['GET', 'POST'])
def delete_wallet():
    if data.instance().is_logged():
        wallet_id = request.args.get('wallet_id')
        if wallet_id.isdecimal():
            user_id = data.instance()._id
            cursor = db.cursor()
            cursor.execute("""SELECT user_id FROM wallets WHERE id={}""".format(wallet_id))
            _fetched_data = cursor.fetchone()
            if user_id == _fetched_data[0]:
                cursor.execute("""DELETE FROM wallets WHERE id={}""".format(wallet_id))
                db.commit()

    return redirect(url_for('views.settings'))


@auth.route('/delete-category', methods=['GET', 'POST'])
def delete_category():
    if data.instance().is_logged():
        category_id = request.args.get('category_id')
        if category_id.isdecimal():
            user_id = data.instance()._id
            cursor = db.cursor()
            cursor.execute("""SELECT user_id FROM expense_categories WHERE id={}""".format(category_id))
            _fetched_data = cursor.fetchone()
            if user_id == _fetched_data[0]:
                cursor.execute("""DELETE FROM expense_categories WHERE id={}""".format(category_id))
                db.commit()

    return redirect(url_for('views.settings'))


@auth.route('/delete-subcategory', methods=['GET', 'POST'])
def delete_subcategory():
    if data.instance().is_logged():
        subcategory_id = request.args.get('subcategory_id')
        if subcategory_id.isdecimal():
            user_id = data.instance()._id
            cursor = db.cursor()
            cursor.execute("""SELECT user_id FROM expense_categories WHERE id={}""".format(subcategory_id))
            _fetched_data = cursor.fetchone()
            if user_id == _fetched_data[0]:
                cursor.execute("""DELETE FROM expense_categories WHERE id={}""".format(subcategory_id))
                db.commit()

    return redirect(url_for('views.settings'))