from flask import Flask

app = Flask(__name__)


@app.route("/")
def index():
    return "你好,世界"


if __name__ == '__main__':
    app.run()