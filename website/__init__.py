import secrets
from flask import Flask
import pymysql


def initialize_database():
    if not check_if_db_and_tables_exists():
        drop_database()
        create_database()
        create_tables()


def check_if_db_and_tables_exists():
    databases = []
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES")
    for database in cursor:
        databases.append(database[0])
    if "expenses_db" not in databases:
        return False
    tables = []
    cursor.execute("SHOW TABLES FROM expenses_db")
    for table in cursor:
        tables.append(table[0])
    if "users" not in tables or "expense_categories" not in tables or"wallets" not in tables or"expenses" not in tables:
        return False
    return True


def drop_database():
    cursor = connection.cursor()
    cursor.execute("DROP DATABASE IF EXISTS expenses_db")


def create_database():
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE expenses_db")


def create_tables():
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE expenses_db.users ( id INT NOT NULL AUTO_INCREMENT, email VARCHAR(30) NOT NULL, password CHAR(88) NOT NULL, PRIMARY KEY (id), UNIQUE (email));")
    cursor.execute("CREATE TABLE expenses_db.expense_categories ( id INT NOT NULL AUTO_INCREMENT, user_id INT NOT NULL, name VARCHAR(30) NOT NULL, parent_id INT, PRIMARY KEY (id),  FOREIGN KEY (parent_id) REFERENCES expense_categories(id) ON DELETE CASCADE, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE expenses_db.wallets ( id INT NOT NULL AUTO_INCREMENT, name VARCHAR(30) user_id INT NOT NULL, amount INT NOT NULL, currency VARCHAR(30) NOT NULL, PRIMARY KEY (id), FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE);")
    cursor.execute("CREATE TABLE expenses_db.expenses (id INT AUTO_INCREMENT, title TEXT, transaction_datetime DATETIME NOT NULL DEFAULT NOW(),  amount INT NOT NULL, wallet_id INT NOT NULL, category_id INT NOT NULL, user_id INT NOT NULL, PRIMARY KEY(id), FOREIGN KEY(wallet_id) REFERENCES wallets(id) ON DELETE CASCADE, FOREIGN KEY(category_id) REFERENCES expense_categories(id) ON DELETE CASCADE, FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);")


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_urlsafe(16)

    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')


    return app



connection = pymysql.connect(host="localhost", user="root", password="")
#drop_database()
initialize_database()
db = pymysql.connect(host="localhost", user="root", password="", database="expenses_db")