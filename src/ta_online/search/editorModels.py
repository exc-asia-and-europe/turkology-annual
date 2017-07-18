# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Enum, DateTime, ForeignKey, String, Float, \
    Boolean
from sqlalchemy.orm import mapper, relation, relationship, composite, scoped_session
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.ext.associationproxy import association_proxy
import inspect
from formattedstring import FormattedString
import sys

if sys.version_info[0] == 2:
    str = unicode  # @UndefinedVariable
    bytes = lambda string, encoding: str(string)


def init(connection='postgresql://postgres:bla@localhost/ta',
         create=False, non_primary=False):
    engine = create_engine(connection)
    metadata = MetaData(engine)
    _map_tables(metadata, engine, non_primary)
    if create:
        metadata.create_all()
    Session = scoped_session(sessionmaker(autoflush=True))
    session = Session()
    """if create:
        for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 21, 22, 24, 25, 26]: # 22-23 was a double volume
            session.add(TAVolume(i, []))
            session.commit()"""
    return session


def _map_tables(metadata, engine, non_primary):
    class LanguageColumn(Column):
        def __init__(self, name):
            super(LanguageColumn, self).__init__(name + 'Id', Integer,
                                                 ForeignKey('languageStrings.id'))

    # table for modification history
    modifications = Table('modifications', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('original_id', Integer),
                          Column('modified_id', Integer, ForeignKey('entries.id')),
                          Column('date', DateTime),
                          Column('user_id', Integer))

    # table for TA volume
    taVolumes = Table('taVolumes', metadata,
                      Column('number', Integer, primary_key=True, autoincrement=False))

    # table for category
    categories = Table('categories', metadata,
                       Column('id', Integer, primary_key=True),
                       LanguageColumn('name'),
                       Column('volume', Integer, ForeignKey('taVolumes.number'), index=True),
                       Column('label', String),
                       LanguageColumn('raw'),
                       Column('scanPage', Integer),
                       Column('nameDE', String),  # XXX
                       Column('nameEN', String),  # XXX
                       Column('scanPosition1_x1', Float),
                       Column('scanPosition1_y1', Float),
                       Column('scanPosition1_x2', Float),
                       Column('scanPosition1_y2', Float),
                       Column('scanPosition2_x1', Float),
                       Column('scanPosition2_y1', Float),
                       Column('scanPosition2_x2', Float),
                       Column('scanPosition2_y2', Float),
                       Column('superCategoryId', Integer, ForeignKey('categories.id')),
                       )

    # tables for entries
    entries = Table('entries', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('position', Integer),
                    Column('type', Enum('monograph', 'monographMagisterthesis',
                                        'monographDissertation', 'article', 'articleRepetition',
                                        'collection', 'collectionRepetition', 'conference', 'bullet',
                                        'bulletContainer', 'unknown', 'placeholder', name='entryType'),
                           nullable=False),
                    Column('volume', Integer, ForeignKey('taVolumes.number'), index=True),
                    Column('number', Integer, index=True),
                    Column('categoryId', Integer, ForeignKey('categories.id'), index=True),
                    LanguageColumn('raw'),
                    Column('problem', Boolean),
                    Column('scanPage', Integer),
                    Column('scanPosition1_x1', Float),
                    Column('scanPosition1_y1', Float),
                    Column('scanPosition1_x2', Float),
                    Column('scanPosition1_y2', Float),
                    Column('scanPosition2_x1', Float),
                    Column('scanPosition2_y1', Float),
                    Column('scanPosition2_x2', Float),
                    Column('scanPosition2_y2', Float))

    monographs = Table('monographs', metadata,
                       Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                       LanguageColumn('title'),
                       Column('university', String),
                       Column('country', String),
                       Column('yearStart', Integer),
                       Column('yearEnd', Integer),
                       Column('yearBracket', Integer),
                       Column('yearAlt', Integer),
                       Column('month', Integer),
                       Column('season', Integer),
                       LanguageColumn('comment'))

    articles = Table('articles', metadata,
                     Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                     LanguageColumn('title'),
                     LanguageColumn('comment'))

    articleRepetitions = Table('articleRepetitions', metadata,
                               Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                               LanguageColumn('title'))

    collections = Table('collections', metadata,
                        Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                        LanguageColumn('title'),
                        Column('volumeStart', Integer),
                        Column('volumeEnd', Integer),
                        Column('volumeBracket', Integer),
                        Column('volumeAlt', Integer),
                        Column('volumeAsterisk', Integer),
                        Column('country', String),
                        Column('yearStart', Integer),
                        Column('yearEnd', Integer),
                        Column('yearBracket', Integer),
                        Column('yearAlt', Integer),
                        Column('month', Integer),
                        Column('season', Integer),
                        LanguageColumn('comment'))

    collectionRepetitions = Table('collectionRepetitions', metadata,
                                  Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                                  LanguageColumn('title'))

    conferences = Table('conferences', metadata,
                        Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                        Column('country', String),
                        Column('startYear', Integer),
                        Column('startMonth', Integer),
                        Column('startDay', Integer),
                        Column('endYear', Integer),
                        Column('endMonth', Integer),
                        Column('endDay', Integer),
                        LanguageColumn('title'),
                        LanguageColumn('comment'))

    bullets = Table('bullets', metadata,
                    Column('id', Integer, ForeignKey('entries.id'), primary_key=True),
                    LanguageColumn('title'),
                    Column('see', Enum('default', 'also', 'under', name='seeType')),
                    LanguageColumn('textReference'))

    subEntries = Table('subEntries', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('parentId', Integer, ForeignKey('entries.id'), index=True),
                       Column('position', Integer),
                       Column('type', Enum('review', 'abstract', 'report', 'unknown',
                                           name='subEntryType'), nullable=False),
                       LanguageColumn('raw'))

    abstracts = Table('abstracts', metadata,
                      Column('id', Integer, ForeignKey('subEntries.id'), primary_key=True),
                      LanguageColumn('title'),
                      Column('yearStart', Integer),
                      Column('yearEnd', Integer),
                      Column('yearBracket', Integer),
                      Column('yearAlt', Integer),
                      Column('month', Integer),
                      Column('season', Integer),
                      LanguageColumn('comment'))

    # tables for other objects
    languageStrings = Table('languageStrings', metadata,
                            Column('id', Integer, primary_key=True),
                            Column('string', String))

    languages = Table('languages', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('parentId', Integer, ForeignKey('languageStrings.id'),
                             index=True),
                      Column('position', Integer),
                      Column('language', Integer))

    persons = Table('persons', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('lastname', String))

    firstnames = Table('firstnames', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('personId', Integer, ForeignKey('persons.id'), index=True),
                       Column('firstname', String),
                       Column('position', Integer))

    cities = Table('cities', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String))

    paginations = Table('paginations', metadata,
                        Column('id', Integer, primary_key=True),
                        Column('parentEntryId', Integer, ForeignKey('entries.id'), index=True),
                        Column('parentSubEntryId', Integer, ForeignKey('subEntries.id'),
                               index=True),
                        Column('position', Integer))

    pages = Table('pages', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('parentId', Integer, ForeignKey('paginations.id'), index=True),
                  Column('position', Integer),
                  Column('pages', Integer),
                  Column('roman', Boolean),
                  Column('bracket', Boolean))

    references = Table('references', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('parentEntryId', Integer, ForeignKey('entries.id'), index=True),
                       Column('parentSubEntryId', Integer, ForeignKey('subEntries.id'),
                              index=True),
                       Column('position', Integer),
                       Column('type', Enum('article', 'ta', name='referenceType'),
                              nullable=False),
                       Column('title', String))

    referenceParts = Table('referenceParts', metadata,
                           Column('id', Integer, primary_key=True),
                           Column('parentId', Integer, ForeignKey('references.id'), index=True),
                           Column('position', Integer),
                           Column('taVolume', Integer),
                           Column('taEntry', Integer),
                           Column('volumeStart', Integer),
                           Column('volumeEnd', Integer),
                           Column('volumeBracket', Integer),
                           Column('volumeAlt', Integer),
                           Column('volumeAsterisk', Integer),
                           Column('issueStart', Integer),
                           Column('issueEnd', Integer),
                           Column('issueBracket', Integer),
                           Column('issueAlt', Integer),
                           Column('issueAsterisk', Integer),
                           Column('subIssueStart', Integer),
                           Column('subIssueEnd', Integer),
                           Column('subIssueBracket', Integer),
                           Column('subIssueAlt', Integer),
                           Column('subIssueAsterisk', Integer),
                           Column('yearStart', Integer),
                           Column('yearEnd', Integer),
                           Column('yearBracket', Integer),
                           Column('yearAlt', Integer),
                           Column('month', Integer),
                           Column('season', Integer),
                           Column('yearPos', Integer),
                           LanguageColumn('comment'))

    pagerefs = Table('pagerefs', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('parentId', Integer, ForeignKey('referenceParts.id'),
                            index=True),
                     Column('position', Integer),
                     Column('start', Integer),
                     Column('end', Integer),
                     Column('roman', Boolean),
                     Column('asterisk', Boolean))

    figures = Table('figures', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('parentId', Integer, ForeignKey('referenceParts.id'),
                           index=True),
                    Column('position', Integer),
                    Column('type', Enum('plate', 'table', 'illustration', 'map',
                                        name='figureType')),
                    Column('start', Integer),
                    Column('end', Integer))

    counts = Table('counts', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('parentId', Integer, ForeignKey('figures.id'), index=True),
                   Column('position', Integer),
                   Column('count', Integer))

    # tables for relations
    entryPersons = Table('entryPersons', metadata,
                         Column('entryId', Integer, ForeignKey('entries.id'), primary_key=True,
                                index=True),
                         Column('personId', Integer, ForeignKey('persons.id'),
                                primary_key=True, index=True),
                         Column('position', Integer))

    entryCities = Table('entryCities', metadata,
                        Column('entryId', Integer, ForeignKey('entries.id'), primary_key=True,
                               index=True),
                        Column('cityId', Integer, ForeignKey('cities.id'), primary_key=True,
                               index=True),
                        Column('position', Integer))

    entryCategories = Table('entryCategories', metadata,
                            Column('entryId', Integer, ForeignKey('entries.id'), primary_key=True,
                                   index=True),
                            Column('newCategoryId', Integer, ForeignKey('categories.id'), primary_key=True,  # XXX
                                   index=True),
                            Column('position', Integer))

    subEntryPersons = Table('subEntryPersons', metadata,
                            Column('subEntryId', Integer, ForeignKey('subEntries.id'),
                                   primary_key=True, index=True),
                            Column('personId', Integer, ForeignKey('persons.id'),
                                   primary_key=True, index=True),
                            Column('position', Integer))

    subEntryCities = Table('subEntryCities', metadata,
                           Column('subEntryId', Integer, ForeignKey('subEntries.id'),
                                  primary_key=True, index=True),
                           Column('cityId', Integer, ForeignKey('cities.id'), primary_key=True,
                                  index=True),
                           Column('position', Integer))

    entryEntries = Table('entryEntries', metadata,
                         Column('sourceEntryId', Integer, ForeignKey('entries.id'),
                                primary_key=True, index=True),
                         Column('entryId', Integer, ForeignKey('entries.id'),
                                primary_key=True, index=True),
                         Column('position', Integer))

    def languageMapper(class_, local_table, *args, **params):
        properties = params.get('properties')
        if properties == None:
            params['properties'.__str__()] = properties = {}
        for column in local_table.get_children():
            if type(column) == LanguageColumn:
                properties[column.name[:-2]] = relationship(LanguageString,
                                                            primaryjoin=column == languageStrings.c.id)
        return mapper(class_, local_table, *args, **params)

    mapper(Modification, modifications)

    # mapper for a volume
    mapper(TAVolume, taVolumes, properties={
        'entries': relationship(Entry,
                                collection_class=ordering_list('position'),
                                order_by=[entries.c.position])}, non_primary=non_primary)

    # mapper for category
    languageMapper(Category, categories, properties={
        'scanPosition1': composite(Position,
                                   categories.c.scanPosition1_x1,
                                   categories.c.scanPosition1_y1,
                                   categories.c.scanPosition1_x2,
                                   categories.c.scanPosition1_y2),
        'scanPosition2': composite(Position,
                                   categories.c.scanPosition2_x1,
                                   categories.c.scanPosition2_y1,
                                   categories.c.scanPosition2_x2,
                                   categories.c.scanPosition2_y2),
        'superCategory': relation(Category, remote_side=[categories.c.id]),
    }, non_primary=non_primary)

    # mappers for entries
    entryMapper = languageMapper(Entry, entries, polymorphic_on=entries.c.type,
                                 properties={
                                     'category': relationship(Category,
                                                              primaryjoin=entries.c.categoryId == categories.c.id),
                                     '_categories': relationship(EntryCategory,
                                                                 collection_class=ordering_list('position'),
                                                                 order_by=[entryCategories.c.position]),
                                     'subEntries': relationship(SubEntry,
                                                                collection_class=ordering_list('position'),
                                                                order_by=[subEntries.c.position]),
                                     'scanPosition1': composite(Position,
                                                                entries.c.scanPosition1_x1,
                                                                entries.c.scanPosition1_y1,
                                                                entries.c.scanPosition1_x2,
                                                                entries.c.scanPosition1_y2),
                                     'scanPosition2': composite(Position,
                                                                entries.c.scanPosition2_x1,
                                                                entries.c.scanPosition2_y1,
                                                                entries.c.scanPosition2_x2,
                                                                entries.c.scanPosition2_y2)
                                 }, non_primary=non_primary)

    monographMapper = languageMapper(Monograph, monographs,
                                     inherits=entryMapper, polymorphic_identity='monograph', properties={
            '_authors': relationship(EntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[entryPersons.c.position]),
            '_cities': relationship(EntryCity,
                                    collection_class=ordering_list('position'),
                                    order_by=[entryCities.c.position]),
            '_categories': relationship(EntryCategory,
                                        collection_class=ordering_list('position'),
                                        order_by=[entryCategories.c.position]),
            'year': composite(Year,
                              monographs.c.yearStart, monographs.c.yearEnd,
                              monographs.c.yearBracket, monographs.c.yearAlt,
                              monographs.c.month, monographs.c.season),
            'paginations': relationship(Pagination,
                                        collection_class=ordering_list('position'),
                                        order_by=[paginations.c.position]),
            '_repetitions': relationship(EntryEntry,
                                         primaryjoin=entries.c.id == entryEntries.c.entryId,
                                         collection_class=ordering_list('position'),
                                         order_by=[entryEntries.c.position])
        }, non_primary=non_primary)

    mapper(MonographMagisterthesis, inherits=monographMapper,
           polymorphic_identity='monographMagisterthesis', non_primary=non_primary)

    mapper(MonographDissertation, inherits=monographMapper,
           polymorphic_identity='monographDissertation', non_primary=non_primary)

    languageMapper(Article, articles, inherits=entryMapper,
                   polymorphic_identity='article', properties={
            '_authors': relationship(EntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[entryPersons.c.position]),
            'references': relationship(Reference,
                                       collection_class=ordering_list('position'),
                                       order_by=[references.c.position]),
            '_repetitions': relationship(EntryEntry,
                                         primaryjoin=entries.c.id == entryEntries.c.entryId,
                                         collection_class=ordering_list('position'),
                                         order_by=[entryEntries.c.position])
        }, non_primary=non_primary)

    languageMapper(ArticleRepetition, articleRepetitions,
                   inherits=entryMapper, polymorphic_identity='articleRepetition',
                   properties={
                       '_authors': relationship(EntryPerson,
                                                collection_class=ordering_list('position'),
                                                order_by=[entryPersons.c.position]),
                       '_references': relationship(EntryEntry,
                                                   primaryjoin=entries.c.id == entryEntries.c.sourceEntryId,
                                                   collection_class=ordering_list('position'),
                                                   order_by=[entryEntries.c.position]),
                       '_repetitions': relationship(EntryEntry,
                                                    primaryjoin=entries.c.id == entryEntries.c.entryId,
                                                    collection_class=ordering_list('position'),
                                                    order_by=[entryEntries.c.position])

                   }, non_primary=non_primary)

    languageMapper(Collection, collections, inherits=entryMapper,
                   polymorphic_identity='collection', properties={
            '_editors': relationship(EntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[entryPersons.c.position]),
            '_cities': relationship(EntryCity,
                                    collection_class=ordering_list('position'),
                                    order_by=[entryCities.c.position]),
            'volumes': composite(Volume,
                                 collections.c.volumeStart, collections.c.volumeEnd,
                                 collections.c.volumeBracket, collections.c.volumeAlt,
                                 collections.c.volumeAsterisk),
            'year': composite(Year,
                              collections.c.yearStart, collections.c.yearEnd,
                              collections.c.yearBracket, collections.c.yearAlt,
                              collections.c.month, collections.c.season),
            'paginations': relationship(Pagination,
                                        collection_class=ordering_list('position'),
                                        order_by=[paginations.c.position]),
            '_repetitions': relationship(EntryEntry,
                                         primaryjoin=entries.c.id == entryEntries.c.entryId,
                                         collection_class=ordering_list('position'),
                                         order_by=[entryEntries.c.position])
        }, non_primary=non_primary)

    languageMapper(CollectionRepetition, collectionRepetitions,
                   inherits=entryMapper, polymorphic_identity='collectionRepetition',
                   properties={
                       '_references': relationship(EntryEntry,
                                                   primaryjoin=entries.c.id == entryEntries.c.sourceEntryId,
                                                   collection_class=ordering_list('position'),
                                                   order_by=[entryEntries.c.position])
                   }, non_primary=non_primary)

    languageMapper(Conference, conferences, inherits=entryMapper,
                   polymorphic_identity='conference', properties={
            '_cities': relationship(EntryCity,
                                    collection_class=ordering_list('position'),
                                    order_by=[entryCities.c.position]),
            'date': composite(ConferenceDate,
                              conferences.c.startYear, conferences.c.startMonth,
                              conferences.c.startDay, conferences.c.endYear,
                              conferences.c.endMonth, conferences.c.endDay),
            '_repetitions': relationship(EntryEntry,
                                         primaryjoin=entries.c.id == entryEntries.c.entryId,
                                         collection_class=ordering_list('position'),
                                         order_by=[entryEntries.c.position])
        }, non_primary=non_primary)

    languageMapper(Bullet, bullets, inherits=entryMapper,
                   polymorphic_identity='bullet', properties={
            '_references': relationship(EntryEntry,
                                        primaryjoin=entries.c.id == entryEntries.c.sourceEntryId,
                                        collection_class=ordering_list('position'),
                                        order_by=[entryEntries.c.position])
        }, non_primary=non_primary)

    mapper(UnknownEntry, inherits=entryMapper,
           polymorphic_identity='unknown', non_primary=non_primary)

    mapper(Placeholder, inherits=entryMapper,
           polymorphic_identity='placeholder', non_primary=non_primary)

    # mappers for subEntries
    subEntryMapper = languageMapper(SubEntry, subEntries,
                                    polymorphic_on=subEntries.c.type, non_primary=non_primary)

    mapper(Review, inherits=subEntryMapper,
           polymorphic_identity='review', properties={
            '_authors': relationship(SubEntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[subEntryPersons.c.position]),
            'references': relationship(Reference,
                                       collection_class=ordering_list('position'),
                                       order_by=[references.c.position])
        }, non_primary=non_primary)

    languageMapper(Abstract, abstracts, inherits=subEntryMapper,
                   polymorphic_identity='abstract', properties={
            '_editors': relationship(SubEntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[subEntryPersons.c.position]),
            '_cities': relationship(SubEntryCity,
                                    collection_class=ordering_list('position'),
                                    order_by=[subEntryCities.c.position]),
            'year': composite(Year,
                              abstracts.c.yearStart, abstracts.c.yearEnd,
                              abstracts.c.yearBracket, abstracts.c.yearAlt,
                              abstracts.c.month, abstracts.c.season),
            'paginations': relationship(Pagination,
                                        collection_class=ordering_list('position'),
                                        order_by=[paginations.c.position]),
        }, non_primary=non_primary)

    mapper(Report, inherits=subEntryMapper,
           polymorphic_identity='report', properties={
            '_authors': relationship(SubEntryPerson,
                                     collection_class=ordering_list('position'),
                                     order_by=[subEntryPersons.c.position]),
            'references': relationship(Reference,
                                       collection_class=ordering_list('position'),
                                       order_by=[references.c.position])
        }, non_primary=non_primary)

    mapper(UnknownSubEntry, inherits=subEntryMapper,
           polymorphic_identity='unknown', non_primary=non_primary)

    # mappers for other objects
    mapper(LanguageString, languageStrings, properties={
        'languages': relationship(Language)}, non_primary=non_primary)
    mapper(Language, languages, non_primary=non_primary)
    mapper(Person, persons, properties={
        'firstnames': relationship(Firstname,
                                   collection_class=ordering_list('position'),
                                   order_by=[firstnames.c.position])}, non_primary=non_primary)
    mapper(Firstname, firstnames, non_primary=non_primary)

    mapper(City, cities, non_primary=non_primary)
    mapper(Pagination, paginations, properties={
        'pagination': relationship(PaginationPages,
                                   collection_class=ordering_list('position'),
                                   order_by=[pages.c.position])}, non_primary=non_primary)
    pageMapper = mapper(PaginationPages, pages, polymorphic_on=pages.c.roman, non_primary=non_primary)
    mapper(ArabicPages, inherits=pageMapper, polymorphic_identity=False, non_primary=non_primary)
    mapper(RomanPages, inherits=pageMapper, polymorphic_identity=True, non_primary=non_primary)

    referenceMapper = mapper(Reference, references,
                             polymorphic_on=references.c.type, properties={
            'referenceParts': relationship(ReferencePart,
                                           collection_class=ordering_list('position'),
                                           order_by=[referenceParts.c.position])}, non_primary=non_primary)

    mapper(ArticleReference, inherits=referenceMapper,
           polymorphic_identity='article', non_primary=non_primary)

    mapper(TAReference, inherits=referenceMapper,
           polymorphic_identity='ta', non_primary=non_primary)

    languageMapper(ReferencePart, referenceParts, properties={
        'volume': composite(Volume,
                            referenceParts.c.volumeStart, referenceParts.c.volumeEnd,
                            referenceParts.c.volumeBracket, referenceParts.c.volumeAlt,
                            referenceParts.c.volumeAsterisk),
        'issue': composite(Volume,
                           referenceParts.c.issueStart, referenceParts.c.issueEnd,
                           referenceParts.c.issueBracket, referenceParts.c.issueAlt,
                           referenceParts.c.issueAsterisk),
        'subIssue': composite(Volume,
                              referenceParts.c.subIssueStart, referenceParts.c.subIssueEnd,
                              referenceParts.c.subIssueBracket, referenceParts.c.subIssueAlt,
                              referenceParts.c.subIssueAsterisk),
        'year': composite(Year,
                          referenceParts.c.yearStart, referenceParts.c.yearEnd,
                          referenceParts.c.yearBracket, referenceParts.c.yearAlt,
                          referenceParts.c.month, referenceParts.c.season),
        'pages': relationship(PageRef,
                              collection_class=ordering_list('position'),
                              order_by=[pagerefs.c.position]),
        'figures': relationship(Figure,
                                collection_class=ordering_list('position'),
                                order_by=[figures.c.position])
    }, non_primary=non_primary)

    pagerefMapper = mapper(PageRef, pagerefs, polymorphic_on=pagerefs.c.roman, non_primary=non_primary)
    mapper(ArabicPageRef, inherits=pagerefMapper, polymorphic_identity=False, non_primary=non_primary)
    mapper(RomanPageRef, inherits=pagerefMapper, polymorphic_identity=True, non_primary=non_primary)

    mapper(Figure, figures, properties={
        'counts': relationship(Count,
                               collection_class=ordering_list('position'),
                               order_by=[counts.c.position])
    }, non_primary=non_primary)

    mapper(Count, counts, non_primary=non_primary)

    # mappers for relations
    mapper(EntryPerson, entryPersons, properties={
        'person': relationship(Person)}, non_primary=non_primary)

    mapper(EntryCity, entryCities, properties={
        'city': relationship(City)}, non_primary=non_primary)

    mapper(EntryCategory, entryCategories, properties={
        'category': relationship(Category)}, non_primary=non_primary)

    mapper(SubEntryPerson, subEntryPersons, properties={
        'person': relationship(Person)}, non_primary=non_primary)
    mapper(SubEntryCity, subEntryCities, properties={
        'city': relationship(City)}, non_primary=non_primary)

    mapper(EntryEntry, entryEntries, properties={
        'sourceEntry': relationship(Entry,
                                    primaryjoin=entryEntries.c.sourceEntryId == entries.c.id),
        'entry': relationship(Entry,
                              primaryjoin=entryEntries.c.entryId == entries.c.id)}, non_primary=non_primary)


class Position(object):
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __composite_values__(self):
        return [self.x1, self.y1, self.x2, self.y2]

    def __set_composite_values__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def __eq__(self, other):
        if type(other) != Position: return False
        return other.x1 == self.x1 and other.y1 == self.y1 and \
               other.x2 == self.x2 and other.y2 == self.y2

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return _repr(self)


class TAVolume(object):
    def __init__(self, number, entries):
        self.number = number
        self.entries = entries

    def __repr__(self):
        return _repr(self)


class Category(object):
    def __init__(self, volume, name, label, raw, scanPage, scanPosition1,
                 scanPosition2, nameDE, nameEN, superCategory):  # XXX

        self.volume = volume
        self.name = languageString(name)
        self.label = label and str(label)
        self.raw = languageString(raw)
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2
        self.nameDE = nameDE  # XXX
        self.nameEN = nameEN  # XXX
        self.superCategory = superCategory

    def __repr__(self):
        return _repr(self)


class Modification(object):
    def __init__(self, original_id, modified_id, date, user_id):
        self.original_id = original_id
        self.modified_id = modified_id
        self.date = date
        self.user_id = user_id


class Entry(object):
    def __init__(self):
        raise NotImplementedError('abstract class')

    def __unicode__(self):
        result = []
        result.append(strip(self._format()))
        for subEntry in self.subEntries:
            result.append(str(subEntry))
        return '\n\t'.join(result)

    def reviews(self):
        return self.getSubEntriesByType("review")

    def reports(self):
        return self.getSubEntriesByType("report")

    def abstracts(self):
        return self.getSubEntriesByType("abstract")

    def getSubEntriesByType(self, type):
        allSubEntries = self.subEntries[:]
        for entry in self.repetitions:
            for subEntry in entry.subEntries:
                allSubEntries.append(subEntry)
        return [subEntry for subEntry in allSubEntries if subEntry.type == type]

    def bullets(self):
        try:
            bullets = [entry for entry in self.repetitions if entry.type == "bullet"]
            return bullets
        except AttributeError:
            return []

    def getCategories(self):
        categories = self.categories[:]
        for bullet in self.bullets():
            for category in bullet.categories:
                categories.append(category)
        return [cat for cat in categories if cat != None]


class Monograph(Entry):
    authors = association_proxy('_authors', 'person')
    cities = association_proxy('_cities', 'city')
    categories = association_proxy('_categories', 'category')
    repetitions = association_proxy('_repetitions', 'sourceEntry')

    def __init__(self, volume, number, authors, title, cities, country, year,
                 paginations, comment, category, subEntries, raw, problem, scanPage,
                 scanPosition1, scanPosition2, categories, repetitions):
        self.volume = volume
        self.number = number
        self.authors = authors
        self.title = languageString(title)
        self.cities = cities
        self.country = country and str(country)
        self.year = year
        self.paginations = paginations
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2
        self.categories = categories
        self.repetitions = repetitions

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s. %s\t%s %s %s', self.number,
                    mapStr(self.authors, ' — '), self.title,
                    ', '.join([item for item in [mapStr(self.cities, '-'),
                                                 self.country, self.year and str(self.year),
                                                 formatPaginations(self.paginations)] if item]), self.comment)


class MonographMagisterthesis(Monograph):
    authors = association_proxy('_authors', 'person')
    cities = association_proxy('_cities', 'city')

    def __init__(self, volume, number, authors, title, university, cities,
                 country, year, paginations, comment, category, subEntries, raw,
                 problem, scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.number = number
        self.authors = authors
        self.title = languageString(title)
        self.university = university and str(university)
        self.cities = cities
        self.country = country and str(country)
        self.year = year
        self.paginations = paginations
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def _format(self):
        raise NotImplementedError()


class MonographDissertation(Monograph):
    authors = association_proxy('_authors', 'person')
    cities = association_proxy('_cities', 'city')

    def __init__(self, volume, number, authors, title, university, cities,
                 country, year, paginations, comment, category, subEntries, raw,
                 problem, scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.number = number
        self.authors = authors
        self.title = languageString(title)
        self.university = university and str(university)
        self.cities = cities
        self.country = country and str(country)
        self.year = year
        self.paginations = paginations
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def _format(self):
        raise NotImplementedError()


class Article(Entry):
    authors = association_proxy('_authors', 'person')
    categories = association_proxy('_categories', 'category')
    repetitions = association_proxy('_repetitions', 'sourceEntry')

    def __init__(self, volume, number, authors, title, references, comment,
                 category, subEntries, raw, problem, scanPage, scanPosition1,
                 scanPosition2, categories, repetitions):
        self.volume = volume
        self.number = number
        self.authors = authors
        self.title = languageString(title)
        self.references = references
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2
        self.categories = categories
        self.repetitions = repetitions

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s. %s\t%s In: %s %s', self.number,
                    mapStr(self.authors, ' — '), self.title,
                    formatReferences(self.references), self.comment)


class ArticleRepetition(Entry):
    authors = association_proxy('_authors', 'person')
    references = association_proxy('_references', 'entry')
    repetitions = association_proxy('_repetitions', 'sourceEntry')

    def __init__(self, volume, number, authors, title, references, category,
                 subEntries, raw, problem, scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.number = number
        self.authors = authors
        self.title = languageString(title)
        self.references = references
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s. %s\t%s %s', self.number,
                    mapStr(self.authors, ' — '), self.title,
                    '[s. TA ' + mapStr(['%s.%s' % (reference.volume, reference.number)
                                        for reference in self.references], ', ') + ']')


class Collection(Entry):
    cities = association_proxy('_cities', 'city')
    editors = association_proxy('_editors', 'person')
    repetitions = association_proxy('_repetitions', 'sourceEntry')

    def __init__(self, volume, number, title, editors, volumes, cities,
                 country, year, paginations, comment, category, subEntries, raw,
                 problem, scanPage, scanPosition1, scanPosition2, repetitions):
        self.volume = volume
        self.number = number
        self.title = languageString(title)
        self.editors = editors
        self.volumes = volumes
        self.cities = cities
        self.country = country and str(country)
        self.year = year
        self.paginations = paginations
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2
        self.repetitions = repetitions

    def __repr__(self):
        return _repr(self)

    def _format(self):
        editors = self.editors and mapStr(self.editors, ' — ', '', True) + \
                                   ' ed. '
        volumes = self.volumes and 'Bd. ' + str(self.volumes) + ', '
        country = self.country and self.country + ', '
        return form('%s. %s %s%s%s, %s%s, %s S. %s', self.number,
                    self.title, editors, volumes, mapStr(self.cities, '-'), country,
                    self.year, mapStr(self.paginations, '; '), self.comment)


class CollectionRepetition(Entry):
    references = association_proxy('_references', 'entry')

    def __init__(self, volume, number, title, references, category, subEntries,
                 raw, problem, scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.number = number
        self.title = languageString(title)
        self.references = references
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s. %s %s', self.number, self.title,
                    '[s. TA ' + mapStr(['%s.%s' % (reference.volume, reference.number)
                                        for reference in self.references], ', ') + ']')


class Conference(Entry):
    cities = association_proxy('_cities', 'city')
    repetitions = association_proxy('_repetitions', 'sourceEntry')

    def __init__(self, volume, number, title, cities, country, date, comment,
                 category, subEntries, raw, problem, scanPage, scanPosition1,
                 scanPosition2, repetitions):
        self.volume = volume
        self.number = number
        self.title = languageString(title)
        self.cities = cities
        self.country = country and str(country)
        self.date = date
        self.comment = languageString(comment)
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2
        self.repetitions = repetitions

    def __repr__(self):
        return _repr(self)

    def _format(self):
        country = self.country and self.country + ', '
        return form('%s. %s, %s%s: %s %s', self.number,
                    mapStr(self.cities, '-'), country, self.date, self.title,
                    self.comment)


class Bullet(Entry):
    references = association_proxy('_references', 'entry')
    categories = association_proxy('_categories', 'category')

    def __init__(self, volume, title, see, references, textReference, categories,  # category,
                 raw, problem, scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.title = languageString(title)
        self.see = see
        self.references = references
        self.textReference = languageString(textReference)
        # self.category = category
        self.categories = categories
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        if self.see == 'default':
            see = form('s. %s', mapStr((reference.number for reference in
                                        self.references), ', '))
        elif self.see == 'also':
            see = form('s. a. %s', mapStr((reference.number for reference in
                                           self.references), ', '))
        elif self.see == 'under':
            see = form('s. u. %s', self.textReference)
        return strip(form('\t• %s, %s', self.title, see))


class UnknownEntry(Entry):
    def __init__(self, volume, number, category, subEntries, raw, problem,
                 scanPage, scanPosition1, scanPosition2):
        self.volume = volume
        self.number = number
        self.category = category
        self.subEntries = subEntries
        self.raw = languageString(raw)
        self.problem = problem
        self.scanPage = scanPage
        self.scanPosition1 = scanPosition1
        self.scanPosition2 = scanPosition2

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s', self.raw)


class Placeholder(Entry):
    def __init__(self, volume, number):
        self.volume = volume
        self.number = number

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return "Placeholder for a missing item which is referenced."


class EntryCategory(object):
    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return _repr(self)


class SubEntry(object):
    def __init__(self):
        raise NotImplementedError('abstract class')

    def __unicode__(self):
        return strip(self._format())


class Review(SubEntry):
    authors = association_proxy('_authors', 'person')

    def __init__(self, authors, references, raw):
        self.authors = authors
        self.references = references
        self.raw = languageString(raw)

    def __repr__(self):
        return _repr(self)

    def _format(self):
        # return form('Rez. %s, %s', mapStr(self.authors, ' — ', '', True),
        return form('%s, %s', mapStr(self.authors, ' — ', '', True),
                    formatReferences(self.references))


class Abstract(SubEntry):
    editors = association_proxy('_editors', 'person')
    cities = association_proxy('_cities', 'city')

    def __init__(self, title, editors, cities, year, paginations, comment,
                 raw):
        self.title = languageString(title)
        self.editors = editors
        self.cities = cities
        self.year = year
        self.paginations = paginations
        self.comment = languageString(comment)
        self.raw = languageString(raw)

    def __repr__(self):
        return _repr(self)

    def _format(self):
        title = self.title and str(self.title) + ' '
        editors = self.editors and mapStr(self.editors, ' — ', '', True) + \
                                   ' ed. '
        comment = self.comment and ' ' + str(self.comment)
        # result  = form('Referate: %s%s%s, %s, %s S.%s', title, editors,
        result = form('%s%s%s, %s, %s S.%s', title, editors,
                      mapStr(self.cities, '-'), self.year,
                      mapStr(self.paginations, '; '), comment)
        if not result.endswith('.'):
            return result + '.'
        return result


class Report(SubEntry):
    authors = association_proxy('_authors', 'person')

    def __init__(self, authors, references, raw):
        self.authors = authors
        self.references = references
        self.raw = languageString(raw)

    def __repr__(self):
        return _repr(self)

    def _format(self):
        authors = self.authors and mapStr(self.authors, ' — ', '', True) + ', '
        # return form('Bericht: %s%s', authors,
        return form('%s%s', authors,
                    formatReferences(self.references))


class UnknownSubEntry(SubEntry):
    def __init__(self, raw):
        self.raw = languageString(raw)

    def __repr__(self):
        return _repr(self)

    def _format(self):
        return form('%s', self.raw)


class Reference(object):
    def __init__(self):
        raise NotImplementedError('abstract class')


class ArticleReference(Reference):
    def __init__(self, title, referenceParts):
        self.title = title and str(title)
        self.referenceParts = referenceParts

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return form('%s %s', self.title, mapStr(self.referenceParts, ', '))


class TAReference(Reference):
    def __init__(self, referenceParts):
        self.referenceParts = referenceParts

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return form('TA %s', mapStr(self.referenceParts, ', '))


class ReferencePart(object):
    def __init__(self, taVolume, taEntry, volume, issue, subIssue, year,
                 yearPos, pages, figures, comment):
        self.taVolume = taVolume
        self.taEntry = taEntry
        self.volume = volume
        self.issue = issue
        self.subIssue = subIssue
        self.year = year
        self.yearPos = yearPos
        self.pages = pages
        self.figures = figures
        self.comment = languageString(comment)

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        items = [item for item in [self.taVolume, intWithUnknown(self.taEntry),
                                   self.volume, self.issue, self.subIssue, mapStr(self.pages, '+',
                                                                                  None)] if item]
        if self.year:
            if type(self.yearPos) == type(None):
                self.yearPos = 0
            items.insert(self.yearPos, self.year)
        result = mapStr(items, '.')
        if self.comment != None:
            result = '%s %s' % (self.comment, result)
        if self.figures != []:
            result = '%s, %s' % (result, mapStr(self.figures, ', '))
        return result


class Person(object):
    def __init__(self, firstnames, lastname):
        self.firstnames = firstnames
        self.lastname = str(lastname)

    def __repr__(self):
        return _repr(self)

    def __unicode__(self, subEntry=False):
        if not self.firstnames:
            return '%s' % self.lastname
        if not subEntry:
            return '%s, %s' % (self.lastname, ' '.join(map(str,
                                                           self.firstnames)))
        return '%s %s' % (' '.join(map(str, self.firstnames)), self.lastname)


class Firstname(object):
    def __init__(self, firstname):
        self.firstname = str(firstname)

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return self.firstname


class EntryPerson(object):
    def __init__(self, person):
        self.person = person

    def __repr__(self):
        return _repr(self)


class EntryCategory(object):
    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return _repr(self)


class SubEntryPerson(object):
    def __init__(self, person):
        self.person = person

    def __repr__(self):
        return _repr(self)


class City(object):
    def __init__(self, name):
        self.name = str(name)

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return self.name


class EntryCity(object):
    def __init__(self, city):
        self.city = city

    def __repr__(self):
        return _repr(self)


class SubEntryCity(object):
    def __init__(self, city):
        self.city = city

    def __repr__(self):
        return _repr(self)


class Comment(object):
    def __init__(self, comment):
        self.comment = comment

    def __repr__(self):
        return _repr()


class Year(object):
    def __init__(self, start, end, bracket, alt, month, season):
        self.start = start
        self.end = end
        self.bracket = bracket
        self.alt = alt
        self.month = month
        self.season = season

    def __composite_values__(self):
        return [self.start, self.end, self.bracket, self.alt, self.month,
                self.season]

    def __set_composite_values__(self, start, end, bracket, alt, month,
                                 season):
        self.start = start
        self.end = end
        self.bracket = bracket
        self.alt = alt
        self.month = month
        self.season = season

    def __eq__(self, other):
        if type(other) != Year: return False
        return self.start == other.start and self.end == other.end and \
               self.bracket == other.bracket and self.alt == other.alt and \
               self.month == other.month and self.season == other.season

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.start != None or self.end != None or self.bracket \
                                                         != None or self.alt != None or self.month != None or self.season \
                                                                                                              != None

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        result = []
        if self.month != None:
            result.append(['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                           'Juli', 'August', 'September', 'Oktober', 'November',
                           'Dezember'][self.month - 1] + ' ')
        if self.season != None:
            result.append(['Frühling', 'Sommer', 'Herbst', 'Winter']
                          [self.season - 1] + ' ')
        if self.start != None:
            if self.start == self.end:
                result.append('%s' % self.start)
            else:
                result.append('%s-%s' % (self.start, self.end))
        if self.bracket != None:
            result.append(' (%s)' % self.bracket)
        if self.alt != None:
            result.append('/%s' % self.alt)
        return ''.join(result)


class Pagination(object):
    def __init__(self, pagination):
        self.pagination = pagination

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return mapStr(self.pagination, '+')


class PaginationPages(object):
    def __init__(self):
        raise NotImplementedError('abstract class')

    def __unicode__(self):
        if self.bracket:
            return '[' + self._formatNumber() + ']'
        return self._formatNumber()


class ArabicPages(PaginationPages):
    def __init__(self, pages, bracket=False):
        self.pages = pages
        self.bracket = bracket

    def __repr__(self):
        return _repr(self)

    def _formatNumber(self):
        return str(self.pages)


class RomanPages(PaginationPages):
    def __init__(self, pages, bracket=False):
        self.pages = pages
        self.bracket = bracket

    def __repr__(self):
        return _repr(self)

    def _formatNumber(self):
        return toRoman(self.pages)


class PageRef(object):
    def __init__(self):
        raise NotImplementedError('abstract class')

    def __unicode__(self):
        if self.start == self.end:
            result = self._formatNumber(self.start)
        else:
            result = '%s-%s' % (self._formatNumber(self.start),
                                self._formatNumber(self.end))
        if self.asterisk:
            return '*' + result + '*'
        return result


class ArabicPageRef(PageRef):
    def __init__(self, start, end, asterisk=False):
        self.start = start
        self.end = end
        self.asterisk = asterisk

    def __repr__(self):
        return _repr(self)

    def _formatNumber(self, number):
        return intWithUnknown(number)


class RomanPageRef(PageRef):
    def __init__(self, start, end, asterisk=False):
        self.start = start
        self.end = end
        self.asterisk = asterisk

    def __repr__(self):
        return _repr(self)

    def _formatNumber(self, number):
        return toRoman(number)


class Volume(object):
    def __init__(self, start, end, bracket, alt, asterisk=False):
        self.start = start
        self.end = end
        self.bracket = bracket
        self.alt = alt
        self.asterisk = asterisk

    def __composite_values__(self):
        return [self.start, self.end, self.bracket, self.alt, self.asterisk]

    def __set_composite_values__(self, start, end, bracket, alt, asterisk):
        self.start = start
        self.end = end
        self.bracket = bracket
        self.alt = alt
        self.asterisk = asterisk

    def __eq__(self, other):
        if type(other) != Year: return False
        return self.start == other.start and self.end == other.end and \
               self.bracket == other.bracket and self.alt == other.alt and \
               self.asterisk == other.asterisk

    def __ne__(self, other):
        return not self.__eq__(other)

    def __bool__(self):
        return self.start != None or self.end != None or self.bracket != None \
               or self.alt != None or self.asterisk != None

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        result = []
        if self.start != None:
            if self.start == self.end:
                result.append(intWithUnknown(self.start))
            else:
                result.append('%s-%s' % (intWithUnknown(self.start),
                                         intWithUnknown(self.end)))
        if self.bracket != None:
            result.append(' (%s)' % intWithUnknown(self.bracket))
        if self.alt != None:
            result.append('/%s' % intWithUnknown(self.alt))
        result = ''.join(result)
        if self.asterisk:
            return '*' + result + '*'
        return result


class Figure(object):
    def __init__(self, type, counts, start, end):
        self.type = type
        self.counts = counts
        self.start = start
        self.end = end

    def __repr__(self):
        return _repr(self)

    mapping = {
        'plate': ('Taf.', 'Taf.'),
        'table': ('Tab.', 'Tab.'),
        'illustration': ('Abb.', 'Abb.'),
        'map': ('Karte', 'Karten')}

    def __unicode__(self):
        result = []
        if self.counts:
            result.append('+'.join([count and str(count) or 'einige' for count
                                    in self.counts]))
            if len(self.counts) == 1 and self.counts[0] == 1:
                result.append(self.mapping[self.type][0])
            else:
                result.append(self.mapping[self.type][1])
        else:
            if self.start == self.end:
                result.append(self.mapping[self.type][0])
                result.append(toRoman(self.start))
            else:
                result.append(self.mapping[self.type][1])
                result.append('%s-%s' % (toRoman(self.start),
                                         toRoman(self.end)))
        return ' '.join(result)


class Count(object):
    def __init__(self, count):
        self.count = count

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        return str(self.count)


class ConferenceDate(object):
    def __init__(self, startYear, startMonth, startDay, endYear, endMonth,
                 endDay):
        self.startYear = startYear
        self.startMonth = startMonth
        self.startDay = startDay
        self.endYear = endYear
        self.endMonth = endMonth
        self.endDay = endDay

    def __composite_values__(self):
        return [self.startYear, self.startMonth, self.startDay, self.endYear,
                self.endMonth, self.endDay]

    def __set_composite_values__(self, startYear, startMonth, startDay,
                                 endYear, endMonth, endDay):
        self.startYear = startYear
        self.startMonth = startMonth
        self.startDay = startDay
        self.endYear = endYear
        self.endMonth = endMonth
        self.endDay = endDay

    def __eq__(self, other):
        if type(other) != ConferenceDate: return False
        return self.startYear == other.startYear and \
               self.startMonth == other.startMonth and \
               self.startDay == other.startDay and \
               self.endYear == other.endYear and \
               self.endMonth == other.endMonth and \
               self.endDay == other.endDay

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return _repr(self)

    def __unicode__(self):
        if self.startDay == None and self.endDay == None:
            if self.startMonth == None and self.endMonth == None:

                # nothing given
                if self.startYear == None and self.endYear == None:
                    return ''

                # only year given
                if self.startYear != self.endYear:
                    return '%s-%s' % (self.startYear, self.endYear)
                return '%s' % self.startYear

            # only year and month given
            if self.startYear != self.endYear:
                return '%s.%s-%s.%s' % (toRoman(self.startMonth),
                                        self.startYear, toRoman(self.endMonth), self.endYear)
            if self.startMonth != self.endMonth:
                return '%s.-%s.%s' % (toRoman(self.startMonth),
                                      toRoman(self.endMonth), self.startYear)
            return '%s.%s' % (toRoman(self.startMonth), self.startYear)

        # year, month and day given
        if self.startYear != self.endYear:
            return '%s.%s.%s-%s.%s.%s' % (self.startDay,
                                          toRoman(self.startMonth), self.startYear, self.endDay,
                                          toRoman(self.endMonth), self.endYear)
        if self.startMonth != self.endMonth:
            return '%s.%s.-%s.%s.%s' % (self.startDay,
                                        toRoman(self.startMonth), self.endDay,
                                        toRoman(self.endMonth), self.startYear)
        if self.startDay != self.endDay:
            return '%s.-%s.%s.%s' % (self.startDay, self.endDay,
                                     toRoman(self.startMonth), self.startYear)
        return '%s.%s.%s' % (self.startDay, toRoman(self.startMonth),
                             self.startYear)


class EntryEntry(object):
    def __init__(self, entry):
        self.entry = entry

    def __repr__(self):
        return _repr(self)

    def attrDict(self):
        attributes = dict(self.__dict__.items()[:])
        for attr in attributes.keys():
            if attr.startswith("_"):
                del attributes[attr]
        return attributes


def languageString(formattedString):
    if formattedString == None: return
    return LanguageString(formattedString)


class LanguageString(object):
    def __new__(cls, *args, **kwargs):
        if len(args) == 1 and args[0] == None: return
        return super(cls, LanguageString).__new__(cls)

    def __init__(self, formattedString):
        if not type(formattedString) == FormattedString:
            formattedString = FormattedString(formattedString)
        self.string = str(formattedString)
        self.languages = []
        oldlang = None
        for pos, lang in enumerate(formattedString.lang):
            if lang != oldlang:
                if lang:
                    try:
                        id = int(lang, 16)
                    except ValueError:
                        print("Error by parsing language id", lang)
                        id = None
                else:
                    id = None
                self.languages.append(Language(pos, id))
            oldlang = lang

    def toFormattedString(self):
        f = FormattedString(self.string)
        lang = []
        oldpos = 0
        langstr = None
        for language in self.languages:
            pos = language.position
            lang.extend((pos - oldpos) * [langstr])
            oldpos = pos
            oldid = language.language
            if oldid:
                langstr = '%04X' % oldid
            else:
                langstr = None
        lang.extend((len(self.string) - oldpos) * [langstr])
        f.lang = lang
        return f

    def __len__(self):
        return len(self.string)

    def __repr__(self):
        return '<LanguageString(%s)>' % repr(self.toFormattedString())

    def __unicode__(self):
        return self.string


class Language(object):
    def __init__(self, position, language):
        self.position = position
        self.language = language

    def __repr__(self):
        return _repr(self)


def _repr(obj):
    return '<%s(%s)>' % (obj.__class__.__name__,
                         ', '.join(['%s=%s' % (arg, repr(getattr(obj, arg)))
                                    for arg in inspect.getargspec(obj.__init__).args[1:]]))


def mapStr(obj, joinChar, default='', *params):
    if obj == None: return default
    # return joinChar.join([item.__unicode__(*params) for item in obj])
    return joinChar.join([unicode(item) for item in obj])


def _replaceNone(obj):
    if obj == None or obj == []: return ''
    return obj


def form(obj, *args):
    return obj % tuple([_replaceNone(item) for item in args])


def strip(str):
    str = str.strip()
    if not str.endswith('.') and not str.endswith(']'): str += '.'
    return str


def formatPaginations(paginations):
    if paginations == None: return
    result = '; '.join(map(str, paginations))
    if result: return result + ' S.'
    return result


def formatReferences(references):
    if references == None: return
    result = ' Auch in: '.join(map(str, references))
    if result and not result.endswith('.'):
        return result + '.'
    return result


romanNumeralMap = (('M', 1000),
                   ('CM', 900),
                   ('D', 500),
                   ('CD', 400),
                   ('C', 100),
                   ('XC', 90),
                   ('L', 50),
                   ('XL', 40),
                   ('X', 10),
                   ('IX', 9),
                   ('V', 5),
                   ('IV', 4),
                   ('I', 1))


def toRoman(n):
    """convert integer to Roman numeral"""
    if n == None: return ''
    if n == 0: return ''
    result = ''
    for numeral, integer in romanNumeralMap:
        while n >= integer:
            result += numeral
            n -= integer
    return result


def intWithUnknown(i):
    if i == None: return
    if i == 0: return ''
    return str(i)
