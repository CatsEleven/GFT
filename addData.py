from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import pytz
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GFT.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(12))
    icon = db.Column(db.String(120), default='default-user.png')  # アイコンフィールドを追加
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(pytz.timezone('Asia/Tokyo')))
    mail = db.Column(db.String)

def add_test_admin():
    hashed_password = generate_password_hash('admin', method='pbkdf2:sha256')
    test_admin = Admin(username='admin', password=hashed_password, mail='hoge@test.com')
    db.session.add(test_admin)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # データベースとテーブルを作成
        add_test_admin()
    print("Test admin added successfully.")
