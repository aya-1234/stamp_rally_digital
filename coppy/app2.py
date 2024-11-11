from flask import Flask, request
import sqlite3
import pandas as pd
#フォルダの下に写真を入れる。
app = Flask(__name__)
#全てのルートからのルーティング　　flask 画像　表示staticフォルダーで表示
@app.route('/')
def hello():
    output='''
<h1>Hello World</h1>
<ul>
<li><a href="/next1">メニュー１</a>
<li><a href="/next2">メニュー２</a>
<li><a href="/next3">メニュー３</a>
<li><a href="/table">テーブル</a>
<li><a href="/enq/ljalkjsdf">アンケート1</a>
<li><a href="/enq/klsjklsdf">アンケート2</a>
</ul>
'''
    return output

@app.route('/next1')
def next1():
    output='''
Next1
<br>
<a href="/">Back</a>
'''
    return output
#ログイン画面
@app.route('/login', methods=['POST'])
def login():
    login_id = request.form.get("loginId")
    with sqlite3.connect('data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM USER WHERE loginId = ?', (login_id,))
        user = cursor.fetchone()

    if user:
        output = f'''
        <h1>ログイン成功</h1>
        <p>ユーザーID: {user[0]}</p>
        <p>ログイン日時: {user[1]}</p>
        <p>使用状況: {'使用済み' if user[2] else '未使用'}</p>
        <br>
        <a href="/">Back</a>
        '''
    else:
        output = '''
        <h1>ログイン失敗</h1>
        <p>ユーザーIDが見つかりません。</p>
        <br>
        <a href="/">Back</a>
        '''
    
    return output

@app.route('/next2')
def next2():
    output='''
Next1
<br>
<a href="/">Back</a>
'''
    return output

@app.route('/next3')
def next3():
    output='''
Next1
<br>
<a href="/">Back</a>
'''
    return output

@app.route('/table')
def table():
    output=''
    with sqlite3.connect('data.db')as conn:
        df = pd.read_sql_query('SELECT * FROM USER',conn)
        output = df.to_html()
    output+='''
<br>Next1
<br>
<a href="/">Back</a>
'''
    return output
#アンケートとボタン作成
enquirely = {
    "ljalkjsdf":("エコポイントとはなんですか？", "回答１", "回答2"),
    "klsjklsdf":("エコな行動は", "水を再利用", "水を捨てる")
}
#上と一緒にルーティングの変数にしてしまう。backでルートに戻る。　インプットでボタンと数字を入れてる。
#form actionで次に飛ばす。keyはルーティングで求められている。nameは必要。CSVから読み込むのもあり。不正解の際はもう１回表示する。
@app.route('/enq/<key>')
def enq(key):
    output=f'''
    {enquirely[key][0]}
<br>
<form action="/ans/{key}" method="POST">
<input type="radio" name="answer" value="1">{enquirely[key][1]}
<input type="radio" name="answer" value="2">{enquirely[key][2]}
<input type="submit">
</form>
<br>
<a href="/">Back</a>
'''
    return output
#回答ans　ルーティングから行ってる。HTTPから受け取るときは文字列だからintにしている。
@app.route('/ans/<key>',methods=["POST"])#ansという関数を使って回答を作る。GETとPOSTを基本使うreturnの前にレスポンスを保存する。
def ans(key):
    ret = request.form.get("answer")
    answer = enquirely[key][int(ret)]
    output=f'''
回答は、{answer}でした。
<br>
<a href="/">Back</a>
'''
    
    return output
@app.route('/user/<int:id>')
def user(id):
    output=''
    with sqlite3.connect('data.db')as conn:
        df = pd.read_sql('SELECT * FROM USER WHERE id=?',conn,params=[id])
        output = df.to_html()
    output+='''
<br>Next1
<br>
<a href="/">Back</a>
'''
    return output

if __name__ == "__main__":
    app.run(debug=True, port=8888, threaded=True)  
