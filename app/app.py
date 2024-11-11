from flask import Flask, render_template, request, redirect, url_for, flash
from init import db
import sqlite3
import pandas as pd
from services.user_service import authenticate_user
from flask_sqlalchemy import SQLAlchemy
from init import db, Login, Stamp



# ... (既存のモデル定義、initialize_db関数などはそのまま)

app = Flask(__name__, template_folder='templates', static_folder='static')

@ app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


# 問題、回答のハッシュ
enquirely = {
     "ljalkjsdf": ("エコポイントとはなんですか？", "回答１", "回答2"),
     "klsjklsdf": ("エコな行動は", "水を再利用", "水を捨てる")
 }


@ app.route("/")
def index():
    enquiry_list = [
         {"key": key, "title": value[0]} for key, value in enquirely.items()
         ]
    return render_template("index.html",
                           enquiry_list=enquiry_list,
                           title=enquirely,
                           other_links=[
                                        {"url": "/admin", "text": "user検索メニュー"},
                                ])



@ app.route('/admin', methods=['GET', 'POST'])
def admin():

    if request.method == 'POST':
        account_name = request.form.get('account')
        if account_name:
            # Accountモデルから検索
            # first()を追加
            db.session.query(Login).filter_by(account=account_name)
            #account = login.query(login).filter_by(account=account_name).first()
            if account_name:
                # 関連するStampデータを取得
                stamps = Stamp.query.filter_by(login_id=account_name).all()  # relationshipを利用
                return render_template('admin.html',
                                       account=account_name,  # accountオブジェクトを渡す
                                       stamps=stamps,    # stampsオブジェクトを渡す
                                       search_results=True)
            else:
                return render_template('admin.html',
                                       error="ユーザーが見つかりません",
                                       search_results=False)
        else:
            return render_template('admin.html',
                                   error="アカウント名を入力してください",
                                   search_results=False)

    else:  # GETリクエストの場合
        return render_template('admin.html', search_results=False)




if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)
