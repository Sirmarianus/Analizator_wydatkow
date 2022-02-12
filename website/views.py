from flask import Blueprint, redirect, render_template, request, flash, url_for
from . import db
from .data import data
from datetime import datetime, date, time


views = Blueprint('views', __name__)


@views.route('/')
def home():
    if data.instance().is_logged():
        _data = data.instance()
        cursor = db.cursor()
        cursor.execute("""SELECT e.id, e.title, e.amount, e.transaction_datetime, ec.name as subcategory, (SELECT name FROM expense_categories WHERE ec.parent_id=id) as category FROM expenses e, expense_categories ec WHERE e.category_id=ec.id AND ec.parent_id IS NOT NULL AND e.wallet_id={} AND e.user_id={} ORDER BY e.transaction_datetime DESC;""".format(_data._active_wallet, _data._id))
        fetched_data = cursor.fetchall()
        return render_template("index.html", fetched_data=fetched_data)
    else:
        return redirect(url_for('auth.login'))


@views.route('/new', methods=['GET', 'POST'])
def new():
    _user_id = data.instance()._id
    cursor = db.cursor()
    if data.instance().is_logged():
        if request.method == 'POST':
            _title = request.form.get('title')
            _title = data.instance().sql_injection_replace(_title)
            _wallet = request.form.get('wallet')
            _wallet = data.instance().sql_injection_replace(_wallet)
            _category = request.form.get('category')
            _category = data.instance().sql_injection_replace(_category)
            _amount = request.form.get('amount')
            _amount = data.instance().sql_injection_replace(_amount)
            _date = request.form.get('date')
            _date = data.instance().sql_injection_replace(_date)
            _time = request.form.get('time')
            _time = data.instance().sql_injection_replace(_time)
            _datetime = datetime.combine(date.fromisoformat(_date), time.fromisoformat(_time))

            if _datetime != '' and _amount != '' and _title != '' and _wallet != '' and _category != '' and _user_id != '':
                cursor.execute("""INSERT INTO expenses (transaction_datetime, amount, title, wallet_id, category_id, user_id) VALUES ("{}", {}, "{}", {}, {}, {});""".format(_datetime, _amount, _title, int(_wallet), int(_category), _user_id))
                db.commit()
        
        cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NULL AND user_id={};""".format(_user_id))
        _categories = cursor.fetchall()
        _subcategories = []
        for ele in _categories:
            cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NOT NULL AND parent_id={} AND user_id={};""".format(ele[0], _user_id))
            _subcategories.append(cursor.fetchall())
        
        cursor.execute("""SELECT id, name FROM wallets WHERE user_id={};""".format(_user_id))
        _wallets = cursor.fetchall()

        return render_template("new.html", categories=_categories, subcategories=_subcategories, wallets=_wallets)
    else:
        return redirect(url_for('auth.login'))


@views.route('/delete', methods=['GET', 'POST'])
def delete():
    expense_id = request.args.get('expense_id')
    if expense_id.isdecimal():
        user_id = data.instance()._id
        cursor = db.cursor()
        cursor.execute("""SELECT user_id FROM expenses WHERE id={}""".format(expense_id))
        if user_id == cursor.fetchone()[0]:
            cursor.execute("""DELETE FROM expenses WHERE id={}""".format(expense_id))
            db.commit()

    return redirect(url_for('views.home'))

