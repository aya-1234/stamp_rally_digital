from app import app

if __name__ == '__main__':
    print("Starting app...") # 起動確認
    app.run(debug=True, port=8888, threaded=True)
