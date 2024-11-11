app.pyファイルの内容


from flask import Flask, request, render_template, flash
from init import db, Login, Checkpoint, Quiz, Quiz_Response, Stamp, Survey, Survey_Choice, Survey_Response
import sqlite3
import pandas as pd
from services.user_service import authenticate_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

initialize_db(app)


@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception:  
        print(f"エラーが発生しました: {exception}")     db.session.remove()

#以下はテーブルが利用可能か確認するコードとページ。
def get_all_logins():
    return db.session.query(Login).all() 

@app.route('/logins', methods=['GET'])
def show_logins():
    try:
        logins = get_all_logins()
        output = '<h1>ログイン情報</h1><ul>'
        for login in logins:
           output += f'<li>ID: {login.id}, アカウント: {login.account}</li>'
        output += '</ul><br><a href="/">Back</a>'
        return output
    except Exception as e:
        return f'<h1>エラーが発生しました</h1><p>{str(e)}</p>'




#これより下はアプリの内容に関してでビジネスロジック、ビューを更新していく。



@app.route('/')
def hello():
    output='''
<h1>Hello World</h1>
<ul>
<li><a href="/logins">ログイン情報</a></li>
<li><a href="/checkpoint/1">チェックポイントログイン</a></li>
</ul>
'''
    return output



####スタート画面:ビジネスロジック

# ログイン画面のルート
@app.route('/checkpoint/<int:checkpoint_id>', methods=['GET', 'POST'])
def login(checkpoint_id):
    if request.method == 'POST':
        account = request.form['account']
        user = Login.query.filter_by(account=account).first()

        # アカウント存在チェック
        if not user:
            flash("アカウントが間違っています", 'error')
            return render_template('login.html', title="ログイン")

        # is_endedのチェック
        if user.is_ended:
            flash("もうスタンプラリーはゴールしています", 'error')
            return render_template('login.html', title="ログイン")

        # is_loggedinのチェック
        if user.is_loggedin:
            return redirect(url_for('main_menu'))

        user.issued_at = datetime.now(pytz.timezone('Asia/Tokyo'))
        if not user.is_used:
            user.is_used = True
        db.session.commit()

        # 同意画面にリダイレクト
        return redirect(url_for('agreement', login_id=user.id))
    # GETメソッドの場合、チェックポイントIDを使用してログイン画面を表示
    return render_template('login.html', title="ログイン", checkpoint_id=checkpoint_id)

@app.route('/agreement/<int:login_id>', methods=['GET', 'POST'])
def agreement(login_id):
    user = Login.query.get(login_id)
    if request.method == 'POST':
        user.is_agree = True
        db.session.commit()

        # STAMPテーブルに新しいレコードを挿入
        new_stamp = Stamp(checkpoint_id=1, login_id=user.id, created_at=datetime.now(pytz.timezone('Asia/Tokyo')))
        db.session.add(new_stamp)
        db.session.commit()

        # アンケート画面にリダイレクト
        return redirect(url_for('survey', checkpoint_id=new_stamp.checkpoint_id))  # 新しく作成したスタンプのcheckpoint_idを使用 # ここで適切なcheckpoint_idを指定

    return render_template('agreement.html', title="同意確認", user=user)

# アンケート画面の表示と回答送信
@app.route('/survey/<int:checkpoint_id>', methods=['GET', 'POST'])
def survey(checkpoint_id):
    user = Login.query.filter_by(is_agree=True).first()  # 同意したユーザーを取得
    if user is None:
        flash("同意が必要です。", 'error')
        return redirect(url_for('login'))  # 同意がない場合はログインページにリダイレクト

    # GETメソッドの場合、質問を取得
    questions = Survey.query.filter_by(checkpoint_id=checkpoint_id)
    print("取得した質問:", questions)
    if request.method == 'POST':
        for question in questions:
            selected_choice_id = request.form.get(f'question_{question.id}')
            choice = Survey_Choice.query.get(selected_choice_id)
            if choice:
                response = Survey_Response(
                    login_id=user.id,
                    survey_id=question.id,
                    value=choice.value,
                    created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
                )
                db.session.add(response)

        # ユーザーのログイン状態を更新
        user.is_loggedin = True
        db.session.commit()
        return redirect(url_for('main_menu'))  # 次のURL

    return render_template('survey.html', title="スタート時アンケート調査", questions=questions)

# メインメニュー画面
@app.route('/main_menu')
def main_menu():
    return render_template('main_menu.html', title="メインメニュー")

#スタンプラリーの参加方法ページ
@app.route('/participation_guide')
def participation_guide():
    return render_template('participation_guide.html', title="スタンプラリーの参加方法")

#スタンプラリーアプリの使い方ページ
@app.route('/app_usage')
def app_usage():
    return render_template('app_usage.html', title="スタンプラリーアプリの使い方")

#ゲット済みのスタンプ確認ページ
@app.route('/view_stamps')
def view_stamps():
    user_id = session.get('login_id')
    if not user_id:
        flash("ログインしてください", 'error')
        return redirect(url_for('login'))

    # 取得済みのスタンプと全チェックポイントの情報を取得
    obtained_stamps = Stamp.query.filter_by(login_id=user_id).all()
    all_checkpoints = Checkpoint.query.all()

    # 取得済みのcheckpoint_idをセットに変換
    obtained_checkpoint_ids = {stamp.checkpoint_id for stamp in obtained_stamps}

    # 全チェックポイントと取得状況をまとめる
    checkpoint_data = []
    for checkpoint in all_checkpoints:
        checkpoint_data.append({
            'name': checkpoint.name,
            'is_obtained': checkpoint.id in obtained_checkpoint_ids
        })

    return render_template('view_stamps.html', title="ゲット済みのスタンプ", checkpoints=checkpoint_data)



####チェックポイント:画面ビジネスロジック





####ゴール画面:ビジネスロジック





