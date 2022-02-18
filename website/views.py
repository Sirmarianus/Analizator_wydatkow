from flask import Blueprint, redirect, render_template, request, flash, url_for
from numpy import zeros
from . import db
from .data import sql_injection_replace
from flask_login import login_required, current_user
from datetime import datetime, date, time
from calendar import monthrange


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    cursor = db.cursor()
    if request.method == 'POST':
        _wallet_id = request.form.get('wallet')
        if _wallet_id.isdecimal():
            cursor.execute("""SELECT user_id FROM wallets WHERE id={}""".format(_wallet_id))
            if int(current_user.id) == cursor.fetchone()[0]:
                cursor.execute("""UPDATE users SET active_wallet={} WHERE id={}""".format(_wallet_id, int(current_user.id)))
                db.commit()
    cursor.execute("""SELECT active_wallet FROM users WHERE id={}""".format(int(current_user.id)))
    active_wallet = cursor.fetchone()[0]

    cursor.execute("""SELECT name, amount, currency FROM wallets WHERE id={}""".format(active_wallet))
    _wallet = cursor.fetchone()

    cursor.execute("""SELECT id, name FROM wallets WHERE user_id={};""".format(int(current_user.id)))
    _wallets = cursor.fetchall()
    
    cursor.execute("""SELECT e.id, e.title, e.amount, e.transaction_datetime, ec.name as subcategory, (SELECT name FROM expense_categories WHERE ec.parent_id=id) as category FROM expenses e, expense_categories ec WHERE e.category_id=ec.id AND ec.parent_id IS NOT NULL AND e.wallet_id={} AND e.user_id={} ORDER BY e.transaction_datetime DESC;""".format(active_wallet, int(current_user.id)))
    _expenses = cursor.fetchall()

    return render_template("index.html", expenses=_expenses, wallets=_wallets, wallet=_wallet)


@views.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    cursor = db.cursor()
    if request.method == 'POST':
        _title = request.form.get('title')
        _wallet = request.form.get('wallet')
        _category = request.form.get('category')
        _amount = request.form.get('amount')
        _date = request.form.get('date')
        _time = request.form.get('time')
        if _title != None and _wallet != None and _category != None and _amount != None and _date != None and _time != None:
            _title = sql_injection_replace(_title)
            _wallet = sql_injection_replace(_wallet)
            _category = sql_injection_replace(_category)
            _amount = sql_injection_replace(_amount)
            _date = sql_injection_replace(_date)
            _time = sql_injection_replace(_time)

            if _date != '' and _time != '' and _amount != '' and _title != '' and _wallet != '' and _category != '' and len(_date) == 8:
                _date = _date[:4] + '-' + _date[4:6] + '-' + _date[6:]
                _datetime = datetime.combine(date.fromisoformat(_date), time.fromisoformat(_time))
                cursor.execute("""INSERT INTO expenses (transaction_datetime, amount, title, wallet_id, category_id, user_id) VALUES ("{}", {}, "{}", {}, {}, {});""".format(_datetime, _amount, _title, int(_wallet), int(_category), int(current_user.id)))
                cursor.execute("""UPDATE wallets SET amount=amount-{} WHERE id={}""".format(_amount, int(_wallet)))
                db.commit()
                
                return redirect(url_for('views.home'))
            else:
                flash("Some fields are empty boii")
        else:
            flash("Some fields are empty boii")

    
    cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NULL AND user_id={};""".format(int(current_user.id)))
    _categories = cursor.fetchall()
    _subcategories = []
    for ele in _categories:
        cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NOT NULL AND parent_id={} AND user_id={};""".format(ele[0], int(current_user.id)))
        _subcategories.append(cursor.fetchall())
    
    cursor.execute("""SELECT id, name FROM wallets WHERE user_id={};""".format(int(current_user.id)))
    _wallets = cursor.fetchall()

    return render_template("new.html", categories=_categories, subcategories=_subcategories, wallets=_wallets)


@views.route('/update', methods=['GET', 'POST'])
@login_required
def update():
    _expense_id = request.args.get('expense_id')
    cursor = db.cursor()
    if request.method == 'POST' and _expense_id.isdecimal():
        cursor.execute("""SELECT user_id FROM expenses WHERE id={}""".format(_expense_id))
        user_id = cursor.fetchone()[0]
        if user_id == int(current_user.id):
            _title = request.form.get('title')
            _title = sql_injection_replace(_title)
            _wallet = request.form.get('wallet')
            _wallet = sql_injection_replace(_wallet)
            _category = request.form.get('category')
            _category = sql_injection_replace(_category)
            _amount = request.form.get('amount')
            _amount = sql_injection_replace(_amount)
            _date = request.form.get('date')
            _date = sql_injection_replace(_date)
            _time = request.form.get('time')
            _time = sql_injection_replace(_time)
            if _date != '' and _time != '' and _amount != '' and _title != '' and _wallet != '' and _category != '' and len(_date) == 8:
                _date = _date[:4] + '-' + _date[4:6] + '-' + _date[6:]
                _datetime = datetime.combine(date.fromisoformat(_date), time.fromisoformat(_time))
                cursor.execute("""UPDATE wallets SET amount=amount+(SELECT amount FROM expenses WHERE id={}) WHERE id={}""".format(_expense_id, int(_wallet)))
                cursor.execute("""DELETE FROM expenses WHERE id={}""".format(_expense_id))
                cursor.execute("""INSERT INTO expenses (transaction_datetime, amount, title, wallet_id, category_id, user_id) VALUES ("{}", {}, "{}", {}, {}, {});""".format(_datetime, _amount, _title, int(_wallet), int(_category), int(current_user.id)))
                cursor.execute("""UPDATE wallets SET amount=amount-{} WHERE id={}""".format(_amount, int(_wallet)))
                db.commit()
            
                return redirect(url_for('views.home'))
        
            else:
                flash("Some fields are empty boii")
        
    cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NULL AND user_id={};""".format(int(current_user.id)))
    _categories = cursor.fetchall()
    _subcategories = []
    for ele in _categories:
        cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NOT NULL AND parent_id={} AND user_id={};""".format(ele[0], int(current_user.id)))
        _subcategories.append(cursor.fetchall())
        
    cursor.execute("""SELECT id, name FROM wallets WHERE user_id={};""".format(int(current_user.id)))
    _wallets = cursor.fetchall()

    if _expense_id.isdecimal():
        cursor.execute("""SELECT id, title, transaction_datetime, amount, wallet_id, category_id, user_id FROM expenses WHERE id={}""".format(_expense_id))
        _fetched_data = cursor.fetchone()
        if int(current_user.id) == _fetched_data[6]:
            _id = _fetched_data[0]
            _title = _fetched_data[1]
            _tansaction_datetime = _fetched_data[2]
            _date = datetime.date(_tansaction_datetime)
            _time = datetime.time(_tansaction_datetime)
            _amount = _fetched_data[3]
            _wallet_id = _fetched_data[4]
            _category_id = _fetched_data[5]
            return render_template("update.html", categories=_categories, subcategories=_subcategories, wallets=_wallets, id=_id, title=_title, date=_date, time=_time, amount=_amount, wallet_id=_wallet_id, category_id=_category_id)
    
    return redirect(url_for('views.home'))


@views.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    cursor = db.cursor()
    cursor.execute("""SELECT id, name, amount, currency FROM wallets WHERE user_id={};""".format(int(current_user.id)))
    _wallets = cursor.fetchall()

    cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NULL AND user_id={};""".format(int(current_user.id)))
    _categories = cursor.fetchall()
    _subcategories = []
    for ele in _categories:
        cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NOT NULL AND parent_id={} AND user_id={};""".format(ele[0], int(current_user.id)))
        _subcategories.append(cursor.fetchall())
    
    cursor.execute("""SELECT email FROM users WHERE id={}""".format(int(current_user.id)))
    _email = cursor.fetchone()

    return render_template('settings.html', wallets=_wallets, categories=_categories, subcategories=_subcategories, email=_email)


@views.route('/charts', methods=['GET', 'POST'])
@login_required
def charts():
    cursor = db.cursor()
    if request.method == 'POST':

        month_number = request.form.get('month_number')
        year_number = request.form.get('year_number')
        category_id = request.form.get('selected-category')
        wallet = request.form.get('wallet')

        if month_number is None or not month_number.isdecimal():
            month_number = int(datetime.today().strftime('%m'))

        if year_number is None or not year_number.isdecimal():   
            year_number = int(datetime.today().strftime('%Y'))

        if wallet is not None and wallet.isdecimal():
            cursor.execute("""UPDATE users SET active_wallet={} WHERE id={}""".format(wallet, int(current_user.id)))
            db.commit()

        if category_id is not None and category_id.isdecimal():
            current_user.category_id = category_id
    no_days = monthrange(year_number, month_number)[1]
    x = list(range(1, no_days+1))
    y = list(zeros(no_days, dtype=int))

    cursor.execute("""SELECT id, name FROM expense_categories WHERE parent_id IS NOT NULL""")
    _categories = cursor.fetchall()

    cursor.execute("""SELECT active_wallet FROM users WHERE id={}""".format(int(current_user.id)))
    active_wallet = cursor.fetchone()[0]
    print(active_wallet)
    cursor.execute("""SELECT transaction_datetime, amount, category_id FROM expenses WHERE wallet_id={} ORDER BY transaction_datetime DESC""".format(active_wallet))
    fetched_data = cursor.fetchall()

    cursor.execute("""SELECT name, amount, currency FROM wallets WHERE id={}""".format(active_wallet))
    _wallet = cursor.fetchone()

    cursor.execute("""SELECT id, name FROM wallets WHERE user_id={};""".format(int(current_user.id)))
    _wallets = cursor.fetchall()

    selected_category = request.form.get('selected-category')
    if selected_category is not None:
        selected_category = int(selected_category)
        for row in fetched_data:
            temp = date.isoformat(datetime.date(row[0]))
            year = int(temp[:4])
            month = int(temp[5:7])
            category = int(row[2])
            if year == year_number and month == month_number:
                if selected_category == 0 or category == selected_category:
                    day = int(temp[8:])
                    amount = int(row[1])
                    y[day-1] += amount
    print(x)
    print(y)
    print(len(y))
    print(len(x))
    print(_wallet)

    return render_template('charts.html', x=x, y=y, categories=_categories, month=month_number, year=year_number, wallets=_wallets, wallet=_wallet)