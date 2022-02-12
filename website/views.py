from flask import Blueprint, redirect, render_template, request, flash, url_for
from . import db
from .data import data

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if data.instance().is_logged():
        _data = data.instance()
        cursor = db.cursor()
        print("""SELECT * FROM expenses WHERE user_id = {} AND wallet_id = {}; """.format(_data._id, _data._active_wallet))
        cursor.execute("""SELECT * FROM expenses WHERE user_id = {} AND wallet_id = {}; """.format(_data._id, _data._active_wallet))
        print(cursor.fetchall())
        return render_template("index.html")
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