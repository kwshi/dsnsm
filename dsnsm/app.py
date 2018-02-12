import os
import flask
app = flask.Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)))
