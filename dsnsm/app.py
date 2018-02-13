import flask
import pprint as pp
import json

import config
from dataentry import DataEntry
from dataman import DataMan

app = flask.Flask('dsnsm')
data = DataMan(config.mongo_url,
               config.mongo_database,
               config.mongo_collection)


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
    if values.get('key') != config.dsnsm_key:
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
    app.run(host=config.host, port=config.port)


if __name__ == '__main__':
    main()
