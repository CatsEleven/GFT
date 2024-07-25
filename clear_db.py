from db import db, create_app
from db import User, Item, Admin, Contact  # 必要に応じてモデルをインポート

def clear_db():
    # テーブルごとに全レコードを削除
    # db.session.query(User).delete()
    db.session.query(Contact).delete()
    # db.session.query(Admin).delete()

    # コミットして変更を保存
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        clear_db()
        print("Database cleared successfully!")
