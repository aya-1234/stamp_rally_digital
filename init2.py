import sqlite3
#一度新しく作ったらDBファイルを削除して更新する。
# データベースの接続とテーブルの作成
def create_tables():
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # CHECKPOINT テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CHECKPOINT (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        p_type TEXT CHECK(p_type IN ('normal', 'start', 'goal')),
        'order' INTEGER
    )
    ''')

    # USER テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS LOGIN (
        id INTEGER PRIMARY KEY,
        issuedAt DATETIME,
        isUsed BOOLEAN,
        loginId TEXT,
        isLoggedin BOOLEAN,
        isAgree BOOLEAN,
        isEnded BOOLEAN
    )
    ''')

    # QUIZ テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS QUIZ (
        id INTEGER PRIMARY KEY,
        checkpoint_id INTEGER,
        order_num DECIMAL,
        content TEXT,
        correct INTEGER,
        answer_1 TEXT,
        answer_2 TEXT,
        answer_3 TEXT,
        FOREIGN KEY (checkpoint_id) REFERENCES CHECKPOINT(id)
    )
    ''')

    # SURVEY テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SURVEY (
        id INTEGER PRIMARY KEY,
        checkpoint_id INTEGER,
        question TEXT,
        survey_order DECIMAL,
        FOREIGN KEY (checkpoint_id) REFERENCES CHECKPOINT(id)
    )
    ''')

    # QUIZ_RESPONSE テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS QUIZ_RESPONSE (
        id INTEGER PRIMARY KEY,
        login_id INTEGER,
        quiz_id INTEGER,
        question_order DECIMAL,
        option_order DECIMAL,
        isCorrected BOOLEAN,
        created DATETIME,
        FOREIGN KEY (login_id) REFERENCES USER(id),
        FOREIGN KEY (quiz_id) REFERENCES QUIZ(id)
    )
    ''')

    # SURVEY_RESPONSE テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SURVEY_RESPONSE (
        id INTEGER PRIMARY KEY,
        login_id INTEGER,
        survey_id INTEGER,
        select_id INTEGER,
        survey_order DECIMAL,
        select_order DECIMAL,
        created DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (login_id) REFERENCES USER(id),
        FOREIGN KEY (survey_id) REFERENCES SURVEY(id),
        FOREIGN KEY (select_id) REFERENCES SURVEY_SELECT(id)
    )
    ''')

    # SURVEY_SELECT テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS SURVEY_SELECT (
        id INTEGER PRIMARY KEY,
        survey_id INTEGER,
        select_text TEXT,
        value integer,
        select_order DECIMAL,
        FOREIGN KEY (survey_id) REFERENCES SURVEY(id)
    )
    ''')

    # STAMP テーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS STAMP (
        id INTEGER PRIMARY KEY,
        checkpoint_id INTEGER,
        login_id INTEGER,
        created DATETIME,
        FOREIGN KEY (checkpoint_id) REFERENCES CHECKPOINT(id),
        FOREIGN KEY (login_id) REFERENCES USER(id)
    )
    ''')

    # 初期データの挿入　　ファーストログインでアクティブにする。
    cursor.execute("INSERT INTO CHECKPOINT (name, description, p_type, order_num) VALUES ('スタート地点', 'この地点からスタンプラリーが始まります。', 'start', 1)")
    cursor.execute("INSERT INTO USER (loginId, issuedAt, isused, isloggedin, isagree, isended) VALUES ('test_user', '2022-01-01 00:00:00', 0, 0, 0, 0)")
    cursor.execute("INSERT INTO QUIZ (checkpoint_id, order_num, content, correct, answer_1, answer_2, answer_3) VALUES (1, 1.0, 'テスト問題', 1, '選択肢1', '選択肢2', '選択肢3')")
    cursor.execute("INSERT INTO SURVEY (checkpoint_id, question, survey_order) VALUES (1, 'テストアンケートの質問', 1.0)")
    cursor.execute("INSERT INTO SURVEY_SELECT (survey_id, select_text, value, select_order) VALUES (1, 'テスト選択肢', 1, 1.0)")
    cursor.execute("INSERT INTO STAMP (checkpoint_id, login_id, created) VALUES (1, 1, '2022-01-01 00:00:00')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()