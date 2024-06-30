from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from db import db, User, Item, Admin, init_app
from PIL import Image
import magic
import uuid
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///GFT.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # アップロードフォルダの設定

# DB初期化
init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.unauthorized_handler
def unauthorized_callback():
    if request.path.startswith('/admin'):
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('login'))

class User(UserMixin):
    def __init__(self, id,username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    admin = Admin.query.get(int(user_id))
    if admin:
        return admin
    
    user = User.query.get(int(user_id))
    if user:
        return user
    
    return None


# 改行するテンプレートを定義する
@app.template_filter('nl2br')
def nl2br(value):
    return Markup(value.replace("\n", "<br>"))


# メンテナンスモードの制御
def get_maintenance_mode():
    with open('settings.json', 'r') as f:
        data = json.load(f)
    return data.get('maintenance_mode', False)


def set_maintenance_mode(status):
    with open('settings.json', 'w') as f:
        json.dump({'maintenance_mode': status}, f)



@app.route('/maintenance')
def maintenance():
    return render_template('users/maintenance.html')



@app.route('/update_status', methods=['POST'])
@login_required
def update_status():
    maintenance_mode = 'maintenance_mode' in request.form
    set_maintenance_mode(maintenance_mode)
    flash('設定が更新されました', 'success')
    return redirect(url_for('admin_index'))


# スーパーユーザー系のルーティング
@app.route('/sudo')
def sudo():
    return render_template('sudo/index.html')


@app.route('/sudo/login', methods=['GET', 'POST'])
def sudo_login():
    USERNAME = 'sudo'
    PASSWORD = 'sudo'
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # if username == USERNAME and password == PASSWORD:
        #     # user = SudoUser(id=1)
        #     # login_user(user)
        #     # return redirect(url_for('sudo'))
        # else:
        #     flash('ユーザー名またはパスワードが違います')
    return render_template('sudo/login.html')

@app.route('/sudo/logout')
@login_required
def sudo_logout():
    logout_user()
    return redirect(url_for('sudo_login'))


# 管理者画面系のルーティング

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        
        admin = Admin.query.filter_by(mail=mail).first()
        
        if admin and check_password_hash(admin.password, password):
            user = User(admin.id, admin.username, 'admin')
            login_user(user)
            return redirect(url_for('admin_index'))
        else:
            flash('メールアドレスかパスワードに誤りがあります')
            return redirect(url_for('admin_login'))
    return render_template('admins/admin-login.html')

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_index():
    maintenance_mode = get_maintenance_mode()
    return render_template('admins/index.html', maintenance_mode=maintenance_mode)

@app.route('/admin/users')
@login_required
def admin_users():
    return render_template('admins/users.html')

@app.route('/admin/items')
@login_required
def admin_items():
    return render_template('admins/items.html')


@app.route('/admin/new', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        thumbnail = request.files['thumbnail']
        image1 = request.files['image1']
        image2 = request.files['image2']
        status = 1
        stock = request.form['stock']


        extension_thumbnail = os.path.splitext(thumbnail.filename)[1]
        extension_image1 = os.path.splitext(image1.filename)[1]
        extension_image2 = os.path.splitext(image2.filename)[1] if image2 else None

        thumbnail_filename = str(uuid.uuid4())+ extension_thumbnail
        image1_filename = str(uuid.uuid4()) + extension_image1
        image2_filename = str(uuid.uuid4()) + extension_image2 if image2 else None

        thumbnail_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnail', thumbnail_filename)
        image1_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image1', image1_filename)
        image2_path = os.path.join(app.config['UPLOAD_FOLDER'], 'image2', image2_filename) if image2 else None

        # ファイルを保存
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        thumbnail.save(thumbnail_path)

        os.makedirs(os.path.dirname(image1_path), exist_ok=True)
        image1.save(image1_path)

        if image2:
            os.makedirs(os.path.dirname(image2_path), exist_ok=True)
            image2.save(image2_path)

        new_item = Item(
            title = name,
            body = description,
            price=price,
            category=category,
            thumbnail=thumbnail_filename,
            image1=image1_filename,
            image2=image2_filename if image2 else None,
            status=status,
            stock = stock
        )
        db.session.add(new_item)
        db.session.commit()

        flash('商品が登録されました！')
        return redirect(url_for('add_item'))

    return render_template('admins/new.html')



@app.route('/admin/items-show')
@login_required
def items_show():
    # items = Item.query.all()
    items = Item.query.filter(Item.status.in_([0, 1, 2])).all()
    return render_template('admins/items-show.html', items=items)


@app.route('/item/edit/<int:item_id>', methods=['GET', 'POST'])
@login_required
def item_edit(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.title = request.form['name']
        item.body = request.form['description']
        item.price = request.form['price']
        item.category = request.form['category']
        item.stock = request.form['stock']
        
        # ファイルアップロード処理
        thumbnail = request.files['thumbnail']
        image1 = request.files['image1']
        image2 = request.files.get('image2')
        
        if thumbnail:
            item.thumbnail = thumbnail.filename
            thumbnail.save(os.path.join(app.config['UPLOAD_FOLDER'], thumbnail.filename))
        
        if image1:
            item.image1 = image1.filename
            image1.save(os.path.join(app.config['UPLOAD_FOLDER'], image1.filename))
        
        if image2:
            item.image2 = image2.filename
            image2.save(os.path.join(app.config['UPLOAD_FOLDER'], image2.filename))
        
        db.session.commit()
        return redirect(url_for('items_show'))
    
    return render_template('admins/item-edit.html', item=item)



@app.route('/admin/change_status/<int:item_id>/<int:new_status>', methods=['POST'])
@login_required
def change_status(item_id, new_status):
    item = Item.query.get_or_404(item_id)
    item.status = new_status
    db.session.commit()
    return jsonify(success=True)


@app.route('/admin/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    item.status = 3
    db.session.commit()
    return jsonify(success=True)

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if request.method == 'POST':
        # アイコンの変更処理
        error = ''
        if 'icon' in request.files and request.files['icon'].filename != '':
            icon = request.files['icon']
            if icon.filename.endswith(('.jpg', '.jpeg', '.png')):
                icon_filename = secure_filename(icon.filename)
                icon_path = os.path.join('static', 'icons/admins', icon_filename)
                os.makedirs(os.path.dirname(icon_path), exist_ok=True)
                icon.save(icon_path)
                current_user.icon = icon_filename
                error = False
            else:
                flash('登録できるファイル形式は jpg, jpeg, png のみです。')
                error = True
                
        
        # パスワードの変更処理
        password = request.form.get('password')
        if password:
            current_user.password = generate_password_hash(password)
        
        if not error:
            db.session.commit()
            flash('設定が更新されました', 'success')
            return redirect(url_for('admin_settings'))

    return render_template('admins/admin-settings.html', user=current_user)



# ユーザーに表示する画面のルーティング
@app.route('/')
def index():
    if get_maintenance_mode():
        return redirect(url_for('maintenance'))
    items = Item.query.filter(Item.category == 'Tops', Item.status == 1, Item.stock >= 1).all()
    return render_template('users/index.html', items=items)

@app.route('/t-shirts')
def shirts():
    items = Item.query.filter(Item.category == 'T-shirts', Item.status == 1, Item.stock >= 1).all()
    return render_template('users/t-shirts.html',  items=items)

@app.route('/Goods')
def Goods():
    items = Item.query.filter(Item.category == 'Goods', Item.status == 1, Item.stock >= 1).all()
    return render_template('users/Goods.html', items=items)


@app.route('/Brand')
def Brand():
    items = Item.query.filter(Item.category == 'Brand', Item.status == 1, Item.stock >= 1).all()
    return render_template('users/Brand.html', items=items)


@app.route('/Tops/<int:item_id>')
def detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('users/detail.html', item=item)

@app.route('/signup')
def signup():
    return render_template('users/signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        if user_id == 'admin':
            user = User(user_id, 'admin')
        else:
            user = User(user_id, 'user')
        login_user(user)
        return redirect(url_for('index'))
    return render_template('login.html')



if __name__ == "__main__":
    app.run(debug=True)
