"""This module takes the parsed data as input and stores this data to a
given database.
"""
from database.database import Abstract, ArabicPageRef, ArabicPages, Article, \
ArticleReference, ArticleRepetition, Bullet, Category, City, \
Collection, CollectionRepetition, Conference, ConferenceDate, Count, Entry, \
Figure, Firstname, Monograph, MonographMagisterthesis, MonographDissertation, \
Pagination, Person, Placeholder, Position, ReferencePart, Report, Review, \
RomanPageRef, RomanPages, TAReference, UnknownEntry, UnknownSubEntry, Volume, \
Year, init
from utils.parsemethod import rawlist

class defaultdict(dict):
    """A dictionary with a default value."""
    def __init__(self, d=None):
        """Initializes the dictionary."""
        if d == None:
            super().__init__()
            self.id = None
        else:
            super().__init__(d)
            self.id = id(d)

    def __getitem__(self, item):
        """Returns the value of the item."""
        result = self.get(item)
        if result and isinstance(result, str):
            result = result.strip()
        if result == '':
            return None
        return result

def factory(func):
    """Factory method for dictionaries with error checking."""
    def decorator(self, input):
        """The related decorator."""
        if input == None:
            return
        if isinstance(input, str):
            self.problem = True
            return
        if isinstance(input, dict):
            input = defaultdict(input)
            if input['problem'] == True:
                self.problem = True
        return func(self, input)
    return decorator

def factoryList(func):
    """Factory method for lists with error checking."""
    def decorator(self, input):
        """The related decorator."""
        result = []
        if input == None:
            return []
        if isinstance(input, str):
            self.problem = True
            return []
        for item in input:
            if isinstance(item, str):
                self.problem = True
                continue
            elif isinstance(item, dict):
                item = defaultdict(item)
                if item['problem'] == True:
                    self.problem = True
            result.append(func(self, item))
        return result
    return decorator

def factoryListRaw(func):
    """Factory method for lists with items which needn't to be further
    processed with error checking.
    """
    def decorator(self, input):
        """The related decorator."""
        result = []
        if input == None:
            return []
        if isinstance(input, str):
            self.problem = True
            return []
        for item in input:
            if isinstance(item, dict):
                item = defaultdict(item)
            result.append(func(self, item))
        return result
    return decorator

def unpack(sequence, argcount):
    """Replaces None with a list with argcount Nones."""
    if sequence == None:
        return [None] * argcount
    return sequence

class Processor(object):
    """Class for converting the parser output to the classes for the
    database.
    """
    def __init__(self, session):
        """Initializes the processor."""
        self.session = session
        self.problem = False
        self.catDict = {}
        self.bulletReferences = []
        self.currentBullet = []
        self.entries = {
            'monograph': self.processMonograph,
            'monographMasterthesis': self.processMonographMagisterthesis,
            'monographDissertation': self.processMonographDissertation,
            'article': self.processArticle,
            'articleRepetition': self.processArticleRepetition,
            'collection': self.processCollection,
            'collectionRepetition': self.processCollectionRepetition,
            'conference': self.processConference,
            'bullet': self.processBullet,
            'unknown': self.processUnknownEntry,
            'unrecognised': self.processUnknownEntry}
        self.subEntries = {
            'reviews': self.processReviews,
            'bericht': self.processReport,
            'referat': self.processAbstract,
            'unrecognised': self.processUnknownSubEntry}

    def process(self, pubs):
        """Processes a list of publications."""
        for position, pub in enumerate(pubs):
            entry = self.processEntry(pub)
            entry.position = position
            self.session.add(entry)
        self.fixBullets()
        self.session.commit()

    @factory
    def processCategory(self, input):
        """Processes a category."""
        category = self.catDict.get(input.id)
        if category == None:
            category = Category(
                input['taVolume'],
                input['catName'],
                input['catLabel'],
                input['raw'],
                input['scanPage'],
                self.processPosition(input['scanPosition1']),
                self.processPosition(input['scanPosition2']))
            self.catDict[input.id] = category
        return category

    @factory
    def processEntry(self, input):
        """Process an entry, calls the specific function."""
        self.problem = False
        type_ = input['type']
        self.volume = input['taVolume']
        if type_ in self.entries:
            result = self.entries[type_](input)
            return result
        self.problem = True
        print('Unkown entry type')

    @factory
    def processMonograph(self, input):
        """Processes a monograph."""
        return Monograph(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processPersons(input['authors']),
            input['title'],
            self.processCities(input['cities']),
            input['country'],
            self.processYear(input['year']),
            self.processPaginations(input['paginations']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processMonographMagisterthesis(self, input):
        """Processes a Magisterarbeit."""
        return MonographMagisterthesis(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processPersons(input['authors']),
            input['title'],
            input['university'],
            self.processCities(input['cities']),
            input['country'],
            self.processYear(input['year']),
            self.processPaginations(input['paginations']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processMonographDissertation(self, input):
        """Processes a dissertation."""
        return MonographDissertation(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processPersons(input['authors']),
            input['title'],
            input['university'],
            self.processCities(input['cities']),
            input['country'],
            self.processYear(input['year']),
            self.processPaginations(input['paginations']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processArticle(self, input):
        """Processes an article."""
        return Article(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processPersons(input['authors']),
            input['title'],
            self.processReferences(input['references']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processArticleRepetition(self, input):
        """Processes an article repetition."""
        return ArticleRepetition(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processPersons(input['authors']),
            input['title'],
            self.processTAEntryReferences(input['references']),
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processCollection(self, input):
        """Processes a collection."""
        return Collection(
            input['taVolume'],
            self.processNumber(input['number']),
            input['title'],
            self.processPersons(input['editors']),
            self.processVolume(input['volumes']),
            self.processCities(input['cities']),
            input['country'],
            self.processYear(input['year']),
            self.processPaginations(input['paginations']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    def processCollectionRepetition(self, input):
        """Processes a collection repetition."""
        return CollectionRepetition(
            input['taVolume'],
            self.processNumber(input['number']),
            input['title'],
            self.processTAEntryReferences(input['references']),
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processConference(self, input):
        """Processes a conference."""
        return Conference(
            input['taVolume'],
            self.processNumber(input['number']),
            input['title'],
            self.processCities(input['cities']),
            input['country'],
            self.processConferenceDate(input['date']),
            input['comment'],
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    @factory
    def processBullet(self, input):
        """Processes a bullet entry."""
        referrer = input['referrer']
        if referrer == 'a':
            see = 'also'
        elif referrer == 'u':
            see = 'under'
        else:
            see = 'default'
        title = input['comment'] and input['comment'].rstrip()
        if title and (title.endswith(',') or title.endswith(':')):
            title = title[:-1].rstrip()
        result = Bullet(
            input['taVolume'],
            title,
            see,
            self.processBulletReferences(input['pointers']),
            input['textPointer'],
            self.processCategory(input['category']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))
        self.currentBullet.append(result)
        return result

    @factory
    def processUnknownEntry(self, input):
        """Processes unknown entry."""
        return UnknownEntry(
            input['taVolume'],
            self.processNumber(input['number']),
            self.processCategory(input['category']),
            self.processSubEntries(input['lineComments']),
            input['raw'],
            self.problem,
            input['scanPage'],
            self.processPosition(input['scanPosition1']),
            self.processPosition(input['scanPosition2']))

    def processSubEntries(self, input):
        """Processes a list of sub entries."""
        result = []
        for item in self._processSubEntries(input):
            if isinstance(item, list):
                result.extend(item)
            else:
                result.append(item)
        return result

    @factoryList
    def _processSubEntries(self, input):
        """Internal helper function for processSubEntries."""
        if isinstance(input, rawlist):
            type_ = 'reviews'
        else:
            type_ = input['type']
        if type_ in self.subEntries:
            return self.subEntries[type_](input)
        print('Unkown sub entry type')

    @factoryList
    def processReviews(self, input):
        """Process a list of reviews."""
        return Review(
            self.processPersons(input['authors']),
            self.processReferences(input['references']),
            input['raw'])

    @factory
    def processReport(self, input):
        """Processes a report."""
        return Report(
            self.processPersons(input['authors']),
            self.processReferences(input['references']),
            input['raw'])

    @factory
    def processAbstract(self, input):
        """Processes an abstract."""
        return Abstract(
            input['title'],
            self.processPersons(input['editors']),
            self.processCities(input['cities']),
            self.processYear(input['year']),
            self.processPaginations(input['paginations']),
            input['comment'],
            input['raw'])

    @factory
    def processUnknownSubEntry(self, input):
        """Processes an unknown sub entry."""
        return UnknownSubEntry(
            input['raw'])

    @factory
    def processNumber(self, input):
        """Processes a number."""
        return input['number']

    @factory
    def processTAVolume(self, input):
        """Processes a TA volume."""
        return input['volume']

    @factory
    def processTAEntry(self, input):
        """Processes a TA entry."""
        return input['entry']

    @factory
    def processVolume(self, input):
        """Processes a volume."""
        return Volume(
            input['volumeStart'],
            input['volumeEnd'],
            input['volumeBracket'],
            input['volumeAlt'],
            input['asterisk'])

    @factoryList
    def processPersons(self, input):
        """Processes a list of persons."""
        return Person(
            self.processFirstnames(input['firstnames']),
            input['lastname'])

    @factoryListRaw
    def processFirstnames(self, input):
        """Processes a list of first names."""
        return Firstname(input)

    @factoryListRaw
    def processCities(self, input):
        """Processes a list of cities."""
        return City(input)

    @factory
    def processYear(self, input):
        """Processes a year."""
        month, season = unpack(self.processYearRange(input['range']), 2)
        return Year(
            input['yearStart'],
            input['yearEnd'],
            input['yearBracket'],
            input['yearAlt'],
            month,
            season)

    @factory
    def processYearRange(self, input):
        """Processes a year range."""
        return input['month'], input['season']

    @factory
    def processConferenceDate(self, input):
        """Processes a conference date."""
        return ConferenceDate(
            input['yearStart'], input['monthStart'], input['dayStart'],
            input['yearEnd'], input['monthEnd'], input['dayEnd'])

    @factoryList
    def processPaginations(self, input):
        """Processes a list of paginations."""
        return Pagination(self.processPaginationPages(input))

    @factoryList
    def processPaginationPages(self, input):
        """Processes a list of pages for a pagination."""
        if input['roman']:
            return RomanPages(input['pages'], bool(input['bracket']))
        return ArabicPages(input['pages'], bool(input['bracket']))

    @factoryList
    def processPageRefs(self, input):
        """Processes a list of page references."""
        if input['roman']:
            return RomanPageRef(
                input['pageStart'],
                input['pageEnd'],
                bool(input['asterisk']))
        return ArabicPageRef(
            input['pageStart'],
            input['pageEnd'],
            bool(input['asterisk']))

    @factoryList
    def processFigures(self, input):
        """Processes a list of figures."""
        ref = input['ref']
        if ref:
            start = ref['figureStart']
            end = ref['figureEnd']
        else:
            start = end = None
        return Figure(
            input['figureType'],
            self.processCounts(input['counts']),
            start,
            end)

    @factoryListRaw
    def processCounts(self, input):
        """Processes a list of counts for a figure."""
        return Count(input)

    @factoryList
    def processReferences(self, input):
        """Processes a list of references."""
        self.referenceCache = defaultdict()
        if input.get('ta'):
            return self._processTAReferences(input)
        return self._processArticleReferences(input)

    def _processArticleReferences(self, input):
        """Processes a list of references to articles."""
        return ArticleReference(
            input['title'],
            self.processReferenceParts(input['referenceParts']))

    def _processTAReferences(self, input):
        """Processes a list of references to TA entries."""
        return TAReference(
            self.processReferenceParts(input['referenceParts']))

    def _cacheReferenceItem(self, input, key):
        """Caches a reference item."""
        item = input[key]
        if item != None:
            self.referenceCache[key] = item
        else:
            item = self.referenceCache[key]
        return item

    @factoryList
    def processReferenceParts(self, input):
        """Processes a list of reference components."""
        return ReferencePart(
            self.processTAVolume(self._cacheReferenceItem(input, 'taVolume')),
            self.processTAEntry(self._cacheReferenceItem(input, 'taEntry')),
            self.processVolume(self._cacheReferenceItem(input, 'volume')),
            self.processVolume(self._cacheReferenceItem(input, 'issue')),
            self.processVolume(self._cacheReferenceItem(input, 'subIssue')),
            self.processYear(self._cacheReferenceItem(input, 'year')),
            self._cacheReferenceItem(input, 'yearPos'),
            self.processPageRefs(self._cacheReferenceItem(input, 'pages')),
            self.processFigures(input['figures']),
            input['comment'])

    def searchReference(self, volume, number):
        """Searches the entry matching the reference. Returns the found
        reference or a placeholder if the entry couldn't be found.
        """
        result = self.session.query(Entry).filter(Entry.volume==volume).filter(
            Entry.number==number).first()
        if result:
            return result
        return Placeholder(volume, number)

    @factoryList
    def processTAEntryReferences(self, input):
        """Processes a reference to a TA entry."""
        return self.searchReference(input['volume'], input['entry'])

    def processBulletReferences(self, input):
        """Processes a reference in a bullet."""
        self.currentBullet = []
        self._processBulletReferences(input)
        return []

    @factoryList
    def _processBulletReferences(self, input):
        """Internal helper function for processBulletReferences."""
        start = input['pointerStart']
        end = input['pointerEnd']
        if start == None or end == None:
            self.problem = True
            return
        self.bulletReferences.append((self.currentBullet, self.volume,
            range(start, end+1)))

    @factory
    def processPosition(self, input):
        """Processes a position."""
        return Position(*input)

    def fixBullets(self):
        """Finds the reference for all bullets."""
        processedReferences = set()
        for entry, volume, references in self.bulletReferences:
            entry = entry[0]
            for reference in references:
                if (entry, reference) in processedReferences:
                    self.problem = True
                else:
                    processedReferences.add((entry, reference))
                    entry.references.append(
                        self.searchReference(volume, reference))
        self.bulletReferences = []

def main():
    """This is the main entry point for storing the parsed data in the
    database."""
    import sys
    import pickle
    filename = sys.argv[1]
    connection = sys.argv[2]
    create = len(sys.argv) > 3
    file = open(filename, 'rb')
    pubs = pickle.load(file)
    file.close()
    session = init(connection=connection, create=create)
    if not create:
        processor = Processor(session)
        processor.process(pubs)

if __name__ == '__main__':
    main()