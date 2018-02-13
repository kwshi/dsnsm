import pymongo as mongo
from dataentry import DataEntry


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
