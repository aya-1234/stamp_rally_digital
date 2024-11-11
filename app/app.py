from flask import Flask, render_template, request, redirect, url_for, flash, session
from init import db, initialize_db, Login, Checkpoint, Quiz, Quiz_Response, Stamp, Survey, Survey_Choice, Survey_Response 
import sqlite3
import pandas as pd
from services.user_service import authenticate_user
from flask_sqlalchemy import SQLAlchemy
import pytz
from datetime import datetime
import os
secret_key = os.urandom(24)


# ... (既存のモデル定義、initialize_db関数などはそのまま)

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)

initialize_db(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    if exception:
        print(f"エラーが発生しました: {exception}")
        db.session.rollback()

def get_all_logins():
    return db.session.query(Login).all() 


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
                                        {"url": "/logins", "text": "ログイン"},
                                        {"url": "/c_all", "text": "chackpoint_all"},
                           ])

@ app.route("/c_all")
def c_all():
    checkpoints = [
        {"name": "スタートポイント", "id": 1},
        {"name": "チェックポイント地点１", "id": 2},
        {"name": "チェックポイント地点２", "id": 3},
        {"name": "チェックポイント地点３", "id": 4},
        {"name": "チェックポイント地点４", "id": 5},
        {"name": "チェックポイント地点５", "id": 6},
        {"name": "チェックポイント地点６", "id": 7},
        {"name": "チェックポイント地点７", "id": 8},
        {"name": "ゴールポイント", "id": 9},
    ]
    return render_template("c_all.html", checkpoints=checkpoints)

#--------------以上はセットアップ-----------------

# テーブルを操作する関数の例
def get_all_logins():
    return db.session.query(Login).all()

@app.route('/logins', methods=['GET'])
def show_logins():
    try:
        logins = get_all_logins()
        return render_template("logins.html", logins=logins)
    except Exception as e:
        return f'<h1>エラーが発生しました</h1><p>{str(e)}</p>'


####3つの共通処理

# ３つのチェックポイントのログイン画面のルート
@app.route('/handle_checkpoint/<int:checkpoint_id>', methods=['GET', 'POST'])
def handle_checkpoint(checkpoint_id):
    if checkpoint_id == 1:
        return login(checkpoint_id)  # IDが1の時はlogin関数を呼び出す
    elif 2 <= checkpoint_id <= 8:
        return checkpoint_login(checkpoint_id)  # IDが2から7の時はcheckpoint_login関数を呼び出す
    elif checkpoint_id == 9:
        return goal_login(checkpoint_id)



    
    # スタートポイントのログイン画面のルート
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

        # ユーザーIDをセッションに保存
        session['user_id'] = user.id

        return redirect(url_for('agreement', login_id=user.id))  # 同意画面にリダイレクト
    # GETメソッドの場合、チェックポイントIDを使用してログイン画面を表示
    return render_template('login.html', title="ログイン", checkpoint_id=checkpoint_id)

# チェックポイントのログイン画面のルート
def checkpoint_login(checkpoint_id):
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
        
        # STAMPテーブル内で同じチェックポイントIDが存在するか確認
        existing_stamp = Stamp.query.filter_by(checkpoint_id=checkpoint_id, login_id=user.id).first()
        if existing_stamp:
            flash("もうスタンプを獲得しました。", 'error')
            return render_template('login.html', title="ログイン")
        
        # ユーザーIDをセッションに保存
        session['user_id'] = user.id
        # チェックポイント画面にリダイレクト
        return redirect(url_for('checkpoint', checkpoint_id=checkpoint_id))
    # GETメソッドの場合、チェックポイントIDを使用してログイン画面を表示
    return render_template('login.html', title="ログイン", checkpoint_id=checkpoint_id)

#ゴール画面のログイン画面のルート
@app.route("/goal_login/<int:checkpoint_id>", methods=["GET", "POST"])
def goal_login(checkpoint_id):
    if request.method == "POST":
        account = request.form["account"]
        user = Login.query.filter_by(account=account).first()
        
        if not user:
            flash("アカウントが間違っています")
            return render_template("login.html", checkpoint_id=checkpoint_id)
        
        # ゴールチェック
        if user.is_ended:
            flash("もうスタンプラリーはゴールしています")
            return render_template("end.html")

        # ログイン状態確認
        if user.is_loggedin:
            return redirect(url_for("show_stamps", user_id=user.id))
        # ユーザーIDをセッションに保存
        session['user_id'] = user.id

    return render_template("login.html", checkpoint_id=checkpoint_id)


# ３つのアンケート画面の表示と回答送信
@app.route('/handle_survey/<int:checkpoint_id>', methods=['GET', 'POST'])
def handle_survey(checkpoint_id):
    user_id = session.get('user_id')
    if checkpoint_id == 1:
        return survey(checkpoint_id)  # IDが1の時はsurvey関数を呼び出す
    elif 2 <= checkpoint_id <= 8:
        return checkpoint_survey(checkpoint_id)  # IDが2から7の時はcheckpoint_survey関数を呼び出す
    elif checkpoint_id == 9:
        return goal_survey(user_id, checkpoint_id)

# スタートポイントのアンケート画面のルート
def survey(checkpoint_id):
    user = Login.query.filter_by(is_agree=True).first()  # 同意したユーザーを取得

    # GETメソッドの場合、質問を取得
    questions = Survey.query.filter_by(checkpoint_id=checkpoint_id).order_by(Survey.survey_order).all()
    print("取得した質問:", questions)
    
    if request.method == 'POST':
        all_selected = True
        for question in questions:
            selected_choice_id = request.form.get(f'question_{question.id}')
            if not selected_choice_id:  # 選択肢が選ばれていない場合
                all_selected = False
                flash(f"質問「{question.question}」に対する選択肢を選んでください。", 'error')
                break
            
            # 選択肢を取得
            choice = Survey_Choice.query.filter_by(id=selected_choice_id, survey_id=question.id).first()
            if choice:
                response = Survey_Response(
                    login_id=user.id,
                    survey_id=question.id,
                    value=choice.value,
                    created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
                )
                db.session.add(response)

        # STAMPテーブルに新しいレコードを挿入
        if all_selected:  # すべての質問に対して選択肢が選ばれた場合
            new_stamp = Stamp(
                checkpoint_id=checkpoint_id,
                login_id=user.id,
                created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
            )
            db.session.add(new_stamp)
            user.is_loggedin = True
            db.session.commit()
            return redirect(url_for('main_menu'))

    return render_template('survey.html', title="スタート時アンケート調査", questions=questions)

# チェックポイントのアンケート画面のルート
def checkpoint_survey(checkpoint_id):
    user_id = session.get('user_id')  # セッションからユーザーIDを取得
    user = Login.query.get(user_id)  # ユーザーを取得
    survey = Survey.query.filter_by(checkpoint_id=checkpoint_id).first()
    choices = Survey_Choice.query.filter_by(survey_id=survey.id).all()

    if request.method == 'POST':
        selected_value = request.form['choice']
        if not selected_value:  # 選択肢が選ばれていない場合
            flash("選択肢を選んでください。", 'error')
            return render_template('survey.html', survey=survey, choices=choices)  # 同じページを再表示
        
        # Survey_Response テーブルに回答結果を記録
        survey_response = Survey_Response(
            login_id=user.id,
            survey_id=survey.id,
            value=selected_value
        )
        db.session.add(survey_response)

        # STAMPテーブルに新しいレコードを挿入
        new_stamp = Stamp(
            checkpoint_id=checkpoint_id,
            login_id=user.id,
            created_at=datetime.now(pytz.timezone('Asia/Tokyo'))
        )
        db.session.add(new_stamp)
        db.session.commit()
        
        return redirect(url_for('view_stamps', checkpoint_id=checkpoint_id))

    return render_template('survey.html', survey=survey, choices=choices)


# ゴールポイントのアンケート画面
@app.route("/goal_survey/<int:user_id>/<int:checkpoint_id>", methods=["GET", "POST"])
def goal_survey(user_id, checkpoint_id):
    user_id = session.get('user_id')
    if request.method == "POST":
        # SURVEY_RESPONSE テーブルに回答を保存
        if not request.form:  # フォームが空の場合
            flash("選択肢を選んでください。", 'error')
            return render_template("survey.html", questions=questions)  # 同じページを再表示
        for selected_choice in request.form.items():
            survey_choice = Survey_Choice.query.get(selected_choice)
            response = Survey_Response(
                login_id=user_id,
                survey_id=survey_choice.survey_id,
                value=survey_choice.value
            )
            db.session.add(response)
        
        # ユーザーの is_ended を True に変更
        user = Login.query.get(user_id)
        user.is_ended = True
        db.session.commit()
        return redirect(url_for("goal"))

    questions = Survey.query.filter_by(checkpoint_id=checkpoint_id).order_by(Survey.survey_order).all()
    return render_template("survey.html", questions=questions)

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



####スタート画面:ビジネスロジック


#同意画面
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
        return redirect(url_for('handle_survey', checkpoint_id=new_stamp.checkpoint_id))  # 新しく作成したスタンプのcheckpoint_idを使用 # ここで適切なcheckpoint_idを指定

    return render_template('agreement.html', title="同意確認", user=user)

#ゲット済みのスタンプ確認ページ
@app.route('/view_stamps')
def view_stamps():
    user_id = session.get('user_id')

    user = Login.query.get(user_id)  # ユーザーを取得
    # 取得済みのスタンプと全チェックポイントの情報を取得
    obtained_stamps = Stamp.query.filter_by(login_id=user.id).all()
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


#チェックポイントの詳細の表示
@app.route('/checkpoint/<int:checkpoint_id>')
def checkpoint(checkpoint_id):
#    user_id = session.get('user_id')
 #   if not user_id:
  #      return redirect(url_for('login', checkpoint_id=checkpoint_id))

    checkpoint = Checkpoint.query.get_or_404(checkpoint_id)
    return render_template('checkpoint.html', checkpoint=checkpoint)

#クイズ画面の表示と回答処理
@app.route('/quiz/<int:checkpoint_id>', methods=['GET', 'POST'])
def quiz(checkpoint_id):
    user_id = session.get('user_id')  # セッションからユーザーIDを取得

    user = Login.query.get(user_id)  # ユーザーを取得
    quiz_order = request.args.get('quiz_order', default=1, type=int)
    quiz = Quiz.query.filter_by(checkpoint_id=checkpoint_id, quiz_order=quiz_order).first()

    if request.method == 'POST':
        answer_selected = request.form['answer']
        if not answer_selected:  # 選択肢が選ばれていない場合
            flash("選択肢を選んでください。", 'error')
            return render_template('quiz.html', quiz=quiz)  # 同じページを再表示
        is_correct = (answer_selected == quiz.correct)

        # Quiz_Response テーブルに回答結果を記録
        quiz_response = Quiz_Response(
            login_id=user.id, 
            quiz_id=quiz.id,
            answer_selected=answer_selected,
            is_corrected=is_correct
        )
        db.session.add(quiz_response)
        db.session.commit()
        
        if is_correct:
            flash("正解です")
            # 次のクイズへの遷移（順次 quiz_order を更新する処理を追加した）
            next_quiz = Quiz.query.filter_by(checkpoint_id=checkpoint_id, quiz_order=quiz_order + 1).first()
            if next_quiz:
                return redirect(url_for('quiz', checkpoint_id=checkpoint_id, quiz_order=quiz_order + 1))
            else:
                flash("全てのクイズが終了しました。")
                return redirect(url_for('handle_survey', checkpoint_id=checkpoint_id))  # チェックポイントのアンケートに遷移
    
    return render_template('quiz.html', quiz=quiz)



####ゴール画面:ビジネスロジック



# スタンプ一覧の表示
@app.route("/stamps/<int:user_id>")
def show_stamps(user_id):
    user_id = session.get('user_id')
    #user = Login.query.get(user_id)
    checkpoints = Checkpoint.query.all()
    user_stamps = {stamp.checkpoint_id for stamp in Stamp.query.filter_by(login_id=user_id).all()}

    # 「アンケートに回答する」ボタンのアクティブ化
    active_survey = all(cp.checkpoint_order == 9 or cp.id in user_stamps for cp in checkpoints)
    return render_template(
        "stamps.html", checkpoints=checkpoints, user_stamps=user_stamps, active_survey=active_survey, user_id=user_id
    )

# ゴール画面
@app.route("/goal")
def goal():
    return render_template("goal.html")







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
