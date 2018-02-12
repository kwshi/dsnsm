import os
import flask
app = flask.Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == '__main__':
    try:
        port = os.environ['PORT']
    except KeyError:
        port = 5000

    app.run(port=os.environ['PORT'])
