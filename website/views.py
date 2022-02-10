from flask import Blueprint, redirect, render_template, request, flash, jsonify, url_for
from flask_login import login_required, current_user
from . import db

views = Blueprint('views', __name__)


@views.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("index.html", user=current_user)
    else:
        return redirect(url_for('auth.login'))