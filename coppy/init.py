from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, Numeric
from datetime import datetime
from sqlalchemy.sql import func
import pytz

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Checkpoint(db.Model):
    __tablename__ = 'CHECKPOINT'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    checkpoint_order = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(240), unique=True, nullable=False)
    checkpoint_type = db.Column(db.String(10), nullable=False)
    __table_args__ = (
        CheckConstraint("checkpoint_type IN ('normal', 'start', 'goal')", name='check_point_type'),
    )


class Login(db.Model):#Update処理で。
    __tablename__ = 'LOGIN'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    is_used = db.Column(db.Boolean, nullable=False)#デフォルト値をFalseにしないと
    account = db.Column(db.String(20), unique=True, nullable=False)
    is_loggedin = db.Column(db.Boolean, nullable=False)
    is_agree = db.Column(db.Boolean, nullable=False)
    is_ended = db.Column(db.Boolean, nullable=False)
    issued_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')), nullable=False)

class Quiz(db.Model):#quiz_orderは３択ではなくCPごとの３つの質問番号。１，２，３，１，２，３のように並べる。
    __tablename__ = 'QUIZ'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('CHECKPOINT.id'), nullable=False)
    quiz_order = db.Column(Numeric(10, 2), unique=True, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    correct = db.Column(db.String(50), nullable=False)
    answer_1 = db.Column(db.String(50), nullable=False)
    answer_2 = db.Column(db.String(50), nullable=False)
    answer_3 = db.Column(db.String(50), nullable=False)

class Quiz_Response(db.Model):
    __tablename__ = 'QUIZ_RESPONSE'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('LOGIN.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('QUIZ.id'), nullable=False)
    answer_selected = db.Column(db.String(50), unique=True, nullable=False)
    is_corrected = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')), nullable=False)

class Stamp(db.Model):
    __tablename__ = 'STAMP'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    login_id = db.Column(db.Integer, db.ForeignKey('LOGIN.id'), nullable=False)
    checkpoint_id = db.Column(db.Integer, db.ForeignKey('CHECKPOINT.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')), nullable=False)

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(pytz.timezone('Asia/Tokyo')), nullable=False)








 #QUIZ_RESPONSEとSTAMPとSURVEY＿RESPONSEは関連集合だから要らない。(必要に応じてどうぞ。）

