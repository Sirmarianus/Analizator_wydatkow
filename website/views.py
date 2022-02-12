from flask import Blueprint, redirect, render_template, request, flash, url_for
from . import db
from .data import data

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if data.instance().is_logged():
        _data = data.instance()
        cursor = db.cursor()
        cursor.execute("""SELECT e.id, e.title, e.ammount, e.transaction_datetime, ec.name as subcategory, (SELECT name FROM expense_categories WHERE ec.parent_id=id) as category FROM expenses e, expense_categories ec WHERE e.category_id=ec.id AND ec.parent_id IS NOT NULL ORDER BY e.transaction_datetime;""")
        fetched_data = cursor.fetchall()
        return render_template("index.html", fetched_data=fetched_data)
    else:
        return redirect(url_for('auth.login'))


@views.route('/new', methods=['GET', 'POST'])
def new():
    if data.instance().is_logged():
        if request.method == 'POST':
            pass
        return render_template("new.html")
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
        else:
            print("Not yours")
    else:
        print("not decimal") 
    return redirect(url_for('views.home'))