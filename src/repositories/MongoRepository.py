import logging
import pymongo


class MongoRepository(object):
    def __init__(self, database_name):
        database = pymongo.MongoClient()[database_name]
        self.paragraphs = database['paragraphs']
        self.citations = database['citations']
        self._create_indexes()

    def _create_indexes(self):
        logging.info('Creating indexes...')
        self.citations.create_index([('volume', 1)])
        self.citations.create_index([('number', 1)])
        self.citations.create_index([('authors', 1)])
        self.citations.create_index([('fullyParsed', 1)])

    def get_citations(self, query=None, limit=10000, skip=0, order_fields=(('volume', True), ('number', True))):
        query = query or {}

        order_fields = [(field_name, {True: pymongo.ASCENDING, False: pymongo.DESCENDING}[ascending]) for field_name, ascending in order_fields]
        return self.citations.find(query).sort(order_fields).skip(skip).limit(limit)

    def insert_citations(self, citations):
        self.citations.insert_many(citations)

    def insert_paragraphs(self, paragraphs):
        self.paragraphs.insert_many(paragraphs)

    def drop_database(self):
        self.paragraphs.drop()
        self.citations.drop()
