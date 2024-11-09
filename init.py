from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Numeric
from datetime import datetime
import sqlite3


# Flaskアプリケーションを初期化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'  # SQLiteのURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# SQLAlchemyのインスタンスを生成
db = SQLAlchemy(app)
#一度新しく作ったらDBファイルを削除して更新する。
# データベースの接続とテーブルの作成
# テーブルの定義
#小数点以上８桁の位、小数点以下第2位まで許容する。
#ログインテーブルのみ大文字あり。
#トランザクションのようにDB関係の操作を保存するセッション。操作の後にコミットと書くことでDBへの操作を行う。
#セッションに追加した後にコミットすることでデータベースへ変更を行う。
#routesとtempratesとserviceによってそのページへ飛ばす。
#db.session.flush()は外部キー制約のあるデータを扱う際にちょこっと設定しておこう。
class Checkpoint(db.Model):
    __tablename__ = 'CHECKPOINT'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(240), unique=True, nullable=False)
    p_type = db.Column(db.String(10), nullable=False)
    __table_args__ = (
        CheckConstraint("p_type IN ('normal', 'start', 'goal')", name='check_p_type'),
    )

class Login(db.Model):#Update処理で。
    __tablename__ = 'LOGIN'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    is_used = db.Column(db.Boolean, nullable=False)#デフォルト値をFalseにしないと
    account = db.Column(db.String(20), unique=True, nullable=False)
    is_loggedin = db.Column(db.Boolean, nullable=False)
    is_agree = db.Column(db.Boolean, nullable=False)
    is_ended = db.Column(db.Boolean, nullable=False)
    issued_at = db.Column(db.DateTime, nullable=False)

class Quiz(db.Model):
    __tablename__ = 'QUIZ'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('CHECKPOINT.id'), nullable=False)
    order = db.Column(Numeric(10, 2), unique=True, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    correct = db.Column(db.String(30), nullable=False)
    answer_1 = db.Column(db.String(50), nullable=False)
    answer_2 = db.Column(db.String(50), nullable=False)
    answer_3 = db.Column(db.String(50), nullable=False)

class Quiz_Response(db.Model):
    __tablename__ = 'QUIZ_RESPONSE'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('LOGIN.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('QUIZ.id'), nullable=False)
    answer_selected = db.Column(Numeric(10, 2), unique=True, nullable=False)
    is_corrected = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class Stamp(db.Model):
    __tablename__ = 'STAMP'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('LOGIN.id'), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('CHECKPOINT.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

class Survey(db.Model):
    __tablename__ = 'SURVEY'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('CHECKPOINT.id'), nullable=False)
    question = db.Column(db.String(120), nullable=False)
    survey_order = db.Column(Numeric(10, 2), unique=True, nullable=False)

class Survey_Choice(db.Model):
    __tablename__ = 'SURVEY_SELECT'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('SURVEY.id'), nullable=False)
    choice = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Integer, nullable=False)

class Survey_Response(db.Model):
    __tablename__ = 'SURVEY_RESPONSE'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('LOGIN.id'), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('SURVEY.id'), nullable=False)
    value = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)



# テストデータを追加する関数
def initialize_db():
    with app.app_context():  # アプリケーションコンテキストを作成
        db.create_all() #テーブル作成

        if db.session.query(Checkpoint).count() == 0:
            # テストデータの作成
            test_checkpoints = [
                Checkpoint(order=1, name="スタート地点", description="この地点からスタンプラリーが始まります。", p_type="start"),
                Checkpoint(order=2, name="地点1番", description="ここは地点１番です。", p_type="normal"),
                Checkpoint(order=3, name="地点2番", description="ここは地点２番です。", p_type="normal"),
                Checkpoint(order=4, name="地点3番", description="ここは地点３番です。", p_type="normal"),
                Checkpoint(order=5, name="ゴール地点", description="ここがゴールです。", p_type="goal")
            ]
            db.session.add_all(test_checkpoints)
            db.session.flush()  # idを生成するためにflushを実行

            test_logins = [
                Login(is_used=False, account="test_user1", is_loggedin=False, is_agree=False, is_ended=False, issued_at=datetime(2022, 1, 1)),
                Login(is_used=False, account="test_user2", is_loggedin=False, is_agree=False, is_ended=False, issued_at=datetime(2022, 1, 2)),
                Login(is_used=False, account="test_user3", is_loggedin=False, is_agree=False, is_ended=False, issued_at=datetime(2022, 1, 3))
            ]
            db.session.add_all(test_logins)
            db.session.flush()  # idを生成するためにflushを実行

            test_quizzes = [
                Quiz(checkpoint_id=test_checkpoints[0].id, order=1.0, content="テスト問題1", correct="1", answer_1="選択肢1", answer_2="選択肢2", answer_3="選択肢3"),
                Quiz(checkpoint_id=test_checkpoints[1].id, order=2.0, content="テスト問題2", correct="2", answer_1="選択肢1", answer_2="選択肢2", answer_3="選択肢3")
            ]
            db.session.add_all(test_quizzes)
            db.session.flush()

            test_surveys = [
                Survey(checkpoint_id=test_checkpoints[0].id, question="テストアンケートの質問1", survey_order=1.0),
                Survey(checkpoint_id=test_checkpoints[1].id, question="テストアンケートの質問2", survey_order=2.0)
            ]
            db.session.add_all(test_surveys)
            db.session.flush()  # idを生成するためにflushを実行

            test_survey_selects = [
                Survey_Choice(survey_id=test_surveys[0].id, choice="選択肢1", value=1),
                Survey_Choice(survey_id=test_surveys[0].id, choice="選択肢2", value=2),
                Survey_Choice(survey_id=test_surveys[1].id, choice="選択肢1", value=1),
                Survey_Choice(survey_id=test_surveys[1].id, choice="選択肢2", value=2 )
            ]
            db.session.add_all(test_surveys)
            db.session.flush()  

            test_stamps = [
                Stamp(login_id=test_logins[0].id, checkpoint_id=test_checkpoints[0].id, created_at=datetime(2022, 1, 1)),
                Stamp(login_id=test_logins[1].id, checkpoint_id=test_checkpoints[1].id, created_at=datetime(2022, 1, 2))
            ]
            db.session.add_all(test_stamps)
            db.session.flush()

            # テーブルに追加し、コミット
#            db.session.add_all(test_checkpoints)
#            db.session.add_all(test_logins)
#            db.session.add_all(test_quizzes)
#            db.session.add_all(test_surveys)
#            db.session.add_all(test_survey_selects)
#            db.session.add_all(test_stamps)

#            db.session.flush() # そのテーブルのIDを確定させる、１つ１つテーブルを作成した後に実行するように設定しないと正常に動作しない。

            db.session.commit()
            print("データベースの初期化とテストデータの追加が完了しました（またはスキップされました）。")
            return

# テーブルを作成する関数
#def create_tables():
#    with app.app_context():  # アプリケーションコンテキストの作成
#        db.create_all()      # テーブルの作成を実行

#if __name__ == "__main__":
#    create_tables()
#    initialize_db()
    # テストデータの追加

# アプリ作成とデータベース初期化
#def create_app():
#    db.init_app(app)
#    return app