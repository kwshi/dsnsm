import os
import flask
import pymongo as mongo
import jinja2 as jj
import time
import pprint as pp

config = {
    # 'db_url': os.environ['DATABASE_URL'], # heroku postgresql
    'mongo_url': os.environ['MONGODB_URI'],
    'mongo_database': 'heroku_hpql25s4',
    'mongo_collection': 'data',
    'host': '0.0.0.0',
    'port': int(os.environ.get('PORT', 5000)),
    'dsnsm_key': os.environ['DSNSM_KEY'],
}


class DataMan:
    def __init__(self, url, database_name, collection_name):
        self.url = url
        self.database_name = database_name
        self.collection_name = collection_name

        self.client = mongo.MongoClient(url)
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def read_all(self):
        return self.collection.find({})

    def write(self,
              name,
              client_timestamp,
              ip,
              message,
              method):
        server_timestamp = time.time()

        entry = {
            'name': name,
            'client_timestamp': client_timestamp,
            'server_timestamp': server_timestamp,
            'message': message,
            'method': method,
            'ip': ip,
        }

        self.collection.insert_one(entry)

        return entry


app = flask.Flask('dsnsm')
data = DataMan(config['mongo_url'],
               config['mongo_database'],
               config['mongo_collection'])


@app.route('/')
def home():
    return flask.Response(pp.pformat(list(data.read_all())),
                          mimetype='text/plain')


@app.route('/submit/<name>', methods=('GET', 'POST'))
def submit(name):
    values = flask.request.values

    if flask.request.is_json():
        values = flask.request.get_json()

    if values.get('key') != config['dsnsm_key']:
        return 'API key mismatch'

    entry = data.write(name=name,
                       client_timestamp=values.get('time'),
                       ip=flask.request.headers.get('X-Forwarded-For'),
                       message=values.get('message'),
                       method=flask.request.method)

    return pp.pformat(entry)


def main():
    app.run(host=config['host'], port=config['port'])


if __name__ == '__main__':
    main()
