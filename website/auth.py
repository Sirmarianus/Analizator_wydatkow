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
        disallowed_chars = "\'\"-!\b\n\r\t\\\%\0"
        for char in disallowed_chars:
            email = email.replace(char, '')
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
        
        disallowed_chars = "\'\"-!\b\n\r\t\\\%\0"
        for char in disallowed_chars:
            email = email.replace(char, '')

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