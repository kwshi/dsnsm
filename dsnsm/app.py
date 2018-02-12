import os
import flask
app = flask.Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


if __name__ == '__main__':
    try:
        port = int(os.environ['PORT'])
        host = os.environ['HOST']
    except KeyError:
        port = 5000
        host = '127.0.0.1'

    app.run(host=host, port=port)
