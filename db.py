from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import UserMixin
from datetime import datetime
import pytz
import os

db = SQLAlchemy()
migrate = Migrate()

def init_app(app):
    db.init_app(app)
    migrate.init_app(app, db)

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GFT.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.urandom(24)

    init_app(app)
    return app


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(12))
    address = db.Column(db.String(200))
    postal_code = db.Column(db.String(20))
    email = db.Column(db.String(120), nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False, default=1)  # 0: 一時停止中, 1: 正常, 2: 退会
    icon = db.Column(db.String(120), default='default-user.png')  # アイコンフィールドを追加
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(pytz.timezone('Asia/Tokyo')))

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    price = db.Column(db.Integer, nullable=False) 
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(pytz.timezone('Asia/Tokyo')))
    status = db.Column(db.Integer, nullable=False, default=1)  # 0: 販売停止, 1: 販売中, 2: 売れた, 3: 削除
    category = db.Column(db.String, nullable=False)  # 直書き
    stock = db.Column(db.Integer)  # 在庫
    thumbnail = db.Column(db.String(120), default='default-item.png')  # アイコンフィールドを追加
    image1 = db.Column(db.String(120), default='default-item.png') 
    image2 = db.Column(db.String(120))  
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Admin(db.Model, UserMixin):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(12))
    icon = db.Column(db.String(120), default='default-user.png')  # アイコンフィールドを追加
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))
    updated_at = db.Column(db.DateTime, onupdate=datetime.now(pytz.timezone('Asia/Tokyo')))
    mail = db.Column(db.String)