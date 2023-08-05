import pycouchdb
import http
import json
import os
from posixpath import join as urljoin
from loguru import logger
import requests
from dstool.class_utils import singleton

@singleton
class pouchDB(object):
    def __init__(self):
        self.couchdb_connection = os.environ.get('DSTOOL_COUCHDB_URL')
        self.couchdb_database = os.environ.get('DSTOOL_COUCHDB_DATABASE')
        self.server = pycouchdb.Server(self.couchdb_connection)
        self.db = self.server.database(self.couchdb_database)

def push_couch(func=None):

    def inner(*args, **kwargs):
        json_data = func(*args, **kwargs)
        db = pouchDB().db
        doc = db.save(json_data)
        logger.info("Pushed to CouchDB: {}".format(doc))
    return inner


if __name__ == "__main__":

    @push_couch
    def test():
        return {'hello': 'world'}
    test()
