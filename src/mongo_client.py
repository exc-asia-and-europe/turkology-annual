import pymongo

def get_database(db_name):
    client = pymongo.MongoClient()
    return client[db_name]
