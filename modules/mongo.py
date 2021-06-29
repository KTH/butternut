import os
import pymongo

URI = os.environ.get('BACKUP_DB_URI')
DATABASE = os.environ.get('BACKUP_DATABASE')
COLLECTION = os.environ.get('BACKUP_COLLECTION')

def get_database_list():
    client = pymongo.MongoClient(URI)
    return client[DATABASE][COLLECTION].find()
