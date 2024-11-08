from app.app import app
from app.init import initialize_db  # initialize_dbをインポート

if __name__ == '__main__':
    initialize_db()  # データベースの初期化、テストデータをテーブルに何もない場合挿入する。
    #データベースの設定やテストデータの挿入に何か知らのコードを追加するなど、変更を加えたらdata.dbのファイルを削除して再度実行。
    app.run(debug=True, port=8888, threaded=True)  
