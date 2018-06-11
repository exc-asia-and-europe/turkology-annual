import bson
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
        self.citations.create_index([('volume', 1), ('number', 1)])
        self.citations.create_index([('authors', 1)])
        self.citations.create_index([('fullyParsed', 1)])
        self.citations.create_index([('_obsolete', 1)])
        self.citations.create_index([
            ('rawText', 'text'),
            ('amendments', 'text'),
            ('keywords', 'text')]
        )

    def get_citation(self, volume=None, number=None, id=None, version=None):
        if id:
            citation = self.citations.find_one({'_id': bson.ObjectId(id)})
        elif None in (volume, number):
            raise ValueError('You must specify either an id or a volume and entry number')
        else:
            search_dict = {'volume': volume, 'number': number}
            citations = list(self.citations.find(search_dict).sort([('_version', pymongo.DESCENDING)]))
            if version:
                version = int(version)
            else:
                version = citations[0]['_version']
            citation = citations[-version]
            citations.remove(citation)
            for historic_citation in citations:
                for attribute in list(historic_citation.keys()):
                    if not attribute.startswith('_'):
                        del historic_citation[attribute]
            citation['_versionHistory'] = citations
        if not citation:
            raise LookupError('Citation with id %s not found', id)
        citation['id'] = id
        return citation

    def find_citations(self, query=None, limit=0, skip=0, order_fields=None, fullyParsed=None):
        if query is None:
            criteria = {}
        else:
            criteria = {'$text': {'$search': query}}
        if fullyParsed is not None:
            criteria['fullyParsed'] = fullyParsed
        criteria['_obsolete'] = {'$ne': True}
        projections = None
        if order_fields:
            order_fields = [(field_name, {True: pymongo.ASCENDING, False: pymongo.DESCENDING}[ascending]) for
                            field_name, ascending in order_fields]
        else:
            if query:
                order_fields = (('score', {'$meta': 'textScore'}),)
                projections = {'score': {'$meta': "textScore"}}
            else:
                order_fields = (('volume', pymongo.ASCENDING), ('number', pymongo.ASCENDING))

        if projections:
            citations = self.citations.find(criteria, projections)
        else:
            citations = self.citations.find(criteria)
        return {
            'data': list(citations.sort(order_fields).skip(skip).limit(limit)),
            'total': self.citations.count(criteria),
        }

    def count_citations(self, criteria=None):
        criteria = criteria or {}
        return self.citations.count(criteria)

    def get_volumes(self):
        return self.citations.distinct("volume")#.sort([('volume', pymongo.ASCENDING)])

    def insert_citations(self, citations):
        self.citations.insert_many(citations)

    def insert_citation(self, citation):
        if '_id' in citation:
            del citation['_id']
        if citation.get('volume') and citation.get('number') and citation.get('_version', 0) > 1:
            self.citations.update({'volume': citation['volume'], 'number': citation['number']}, {'$set': {'_obsolete': True}})
        self.citations.insert_one(citation)

    def insert_paragraphs(self, paragraphs):
        self.paragraphs.insert_many(paragraphs)

    def drop_database(self):
        self.paragraphs.drop()
        self.citations.drop()
