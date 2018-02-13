import os
import flask
import pymongo as mongo
import jinja2 as jj
import time
import pprint as pp
import json

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
        for entry_dict in self.collection.find():
            yield DataEntry(**entry_dict)

    def write(self, entry):
        self.collection.insert_one(dict(entry))


class DataError(Exception):
    def __init__(self, key, message):
        self.key = key
        self.message = message

    def __str__(self):
        return 'DataError for key `{}`: {}'.format(self.key,
                                                   self.message)


class DataEntry:
    def __init__(self,
                 name,
                 client_timestamp,
                 server_timestamp,
                 message,
                 method,
                 ip,
                 _id=None):
        self.name = name
        self.client_timestamp = client_timestamp
        self.server_timestamp = server_timestamp
        self.message = message
        self.method = method
        self.ip = ip

    @classmethod
    def from_request(cls, name, request):
        values = request.values

        if request.is_json:
            values = request.get_json()

        try:
            client_timestamp = int(values.get('time'))
        except ValueError:
            raise DataError('client_timestamp',
                            'Invalid timestamp (integer conversion failed)')
            client_timestamp = -1

        server_timestamp = int(time.time())

        message = values.get('message', '')

        return cls(name=name,
                   client_timestamp=client_timestamp,
                   server_timestamp=server_timestamp,
                   message=message,
                   method=request.method,
                   ip=request.headers.get('X-Forwarded-For',
                                          request.remote_addr))

    def __iter__(self):
        yield from (('name', self.name),
                    ('client_timestamp', self.client_timestamp),
                    ('server_timestamp', self.server_timestamp),
                    ('message', self.message),
                    ('method', self.method),
                    ('ip', self.ip))


app = flask.Flask('dsnsm')
data = DataMan(config['mongo_url'],
               config['mongo_database'],
               config['mongo_collection'])


@app.route('/fetch/raw')
def fetch_raw():
    return flask.Response(pp.pformat(tuple(map(dict,
                                               data.read_all()))),
                          mimetype='text/plain')


@app.route('/fetch/raw/min')
def fetch_raw_min():
    return flask.Response(str(tuple(map(dict,
                                        data.read_all()))),
                          mimetype='text/plain')


@app.route('/fetch/json')
def fetch_json():
    return flask.Response(json.dumps(tuple(map(dict,
                                               data.read_all())),
                                     indent=2,
                                     sort_keys=True),
                          mimetype='application/json')


@app.route('/fetch/json/min')
def fetch_json_min():
    return flask.Response(json.dumps(tuple(map(dict,
                                               data.read_all())),
                                     separators=(',', ':')),
                          mimetype='application/json')


@app.route('/submit/<name>', methods=('GET', 'POST'))
def submit(name):
    values = flask.request.values

    if flask.request.is_json:
        values = flask.request.get_json()

    # check api key
    if values.get('key') != config['dsnsm_key']:
        return flask.Response('API key mismatch',
                              mimetype='text/plain'), 403

    try:
        entry = DataEntry.from_request(name, flask.request)

    except DataError as error:
        return str(error), 400

    data.write(entry)

    return flask.Response(pp.pformat(dict(entry)),
                          mimetype='text/plain'), 201


def main():
    app.run(host=config['host'], port=config['port'])


if __name__ == '__main__':
    main()
