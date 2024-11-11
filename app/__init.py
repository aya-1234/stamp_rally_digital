from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config.Config')  # 設定ファイルを読み込む

db = SQLAlchemy(app)

from app import routes, models # routes, modelsをインポート

# ... その他の初期化処理 (Blueprintの登録など) ...