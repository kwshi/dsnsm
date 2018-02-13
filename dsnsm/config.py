import os

mongo_url = os.environ['MONGODB_URI']
mongo_database = 'heroku_hpql25s4'
mongo_collection = 'data'
host = '0.0.0.0'
port = int(os.environ.get('PORT', 5000))
dsnsm_key = os.environ['DSNSM_KEY']
