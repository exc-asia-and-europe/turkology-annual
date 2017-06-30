from operator import itemgetter
import lucene

from analyzers import PorterStemmerAnalyzer

from java.io import File
from java.util import Locale
from org.apache.lucene.search import IndexSearcher, Sort, SortField, MatchAllDocsQuery
from org.apache.lucene.index import IndexReader
from org.apache.lucene.search.highlight import Highlighter, SimpleHTMLFormatter, QueryScorer
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import MMapDirectory

from ta_online import settings
from django.utils import translation


def _(bla):
    return bla


vm = lucene.initVM(lucene.CLASSPATH)

#    Name        Darstellung        Suchkriterium    Sortierkriterium
fields = (
    ("freetext", _("Freitext"), True, False),
    ("relevance", _("Relevanz"), False, True),
    ("title", _("Titel"), True, True),
    ("author", _("Autor"), True, True),
    ("city", _("Ort"), True, True),
    ("year", _("Jahr"), True, True),
    ("category", _("Schlagwort"), True, True),
    ("volume", _("TA Band"), True, True),
    ("journal", _("Zeitschrift"), True, True),
)

conjunctions = (
    ("AND", _("und")),
    ("OR", _("oder")),
    ("NOT", _("nicht")),
)


class Field():
    def __init__(self, name, repr, searchable, sortable):
        self.name = name
        self.repr = repr
        self.searchable = searchable
        self.sortable = sortable

    def __unicode__(self):
        return self.repr


fields = [Field(field[0], field[1], field[2], field[3]) for field in fields]


class Hit():
    def __init__(self, id, volume, number, title, author, city, year, categories, pubtype, score):
        self.volume = volume
        self.number = number
        self.id = int(id)
        self.title = title
        self.author = author
        self.city = city
        self.year = year
        self.categories = categories
        self.pubtype = pubtype
        self.score = score


class TASearcher():
    def __init__(self, queries=[], criteria=[], conjunctions=[], orderby=["ta"], ascending=True, limit=10000):
        vm.attachCurrentThread()

        self.queries = [query for query in queries if len(query.strip()) > 0]
        self.criteria = criteria
        self.conjunctions = conjunctions
        self.orderby = orderby
        self.ascending = ascending
        self.queryString = ""
        self.limit = limit

        self.fields = fields
        self.analyzer = PorterStemmerAnalyzer()
        self.queryParser = QueryParser(Version.LUCENE_30, "freetext", self.analyzer)
        self.queryParser.setAllowLeadingWildcard(True)
        self.queryParser.setDefaultOperator(QueryParser.Operator.AND)
        indexDir = settings.LUCENE_INDEX_DIRECTORY
        self.index = MMapDirectory(File(indexDir))

    def createQueryString(self):
        # Simple
        if len(self.criteria) == 0:
            self.queryString = "(%s) OR freetext-normalized:(%s)" % (self.queries[0], self.queries[0])
        # Advanced
        else:
            queryPairs = []
            criteriaQueries = zip(self.criteria, self.queries)
            self.criteria = dict(criteriaQueries).keys()
            for criterion, query in criteriaQueries:
                if criterion in ("volume", "number", "category-label", "pubtype", "author-sort"):
                    queryPairs.append("%s:%s" % (criterion, query))
                elif criterion == "year":
                    queryPairs.append("year-start:%s OR year-end:%s" % (query, query))
                else:
                    queryPairs.append('%s:%s OR %s-normalized:%s' % (criterion, query, criterion, query))
            # queryPairs = ["%s:%s"%(criterion,query.replace(" ", "+")) for criterion, query in zip(criteria, queries)]
            try:
                queryString = "%s %s" % (queryPairs[0], " ".join(
                    ["%s (%s)" % (conj, pair) for conj, pair in zip(self.conjunctions, queryPairs[1:])]))
                self.queryString = queryString
                return queryString
            except:
                self.queryString = "freetext"
                return self.queryString

    def getQueryString(self):
        return self.queryString

    def _getHits(self):
        reader = IndexReader.open(self.index)
        searcher = IndexSearcher(reader)

        # Sortierung nach Band- und Eintragsnummer (4: Wert als Integer behandeln)
        sortDict = {
            "ta": (("volume", SortField.Type.INT), ("number", SortField.Type.INT)),
            "year": (("year-start", SortField.Type.INT), ("year-end", SortField.Type.INT)),
            "author-title": (("author-sort", SortField.Type.STRING), ("title-sort", SortField.Type.STRING)),
            "title": (("title-sort", Locale.GERMAN),),
            "author": (("author-sort", Locale.GERMAN),),
        }

        sortFields = []

        reverse = not self.ascending

        for name in self.orderby:
            for fieldName, typeNum in sortDict.get(name, []):
                sortFields.append(SortField(fieldName, typeNum, reverse))

        if len(sortFields) == 0:
            sortFields = [SortField("volume", SortField.Type.INT), SortField("number", SortField.Type.INT)]

        sort = Sort(sortFields)

        topDocs = searcher.search(self.query, None, 80000, sort)
        hits = topDocs.scoreDocs
        self.hits = hits
        self.searcher = searcher

        lang = translation.get_language()
        if lang != "de":
            lang = "en"

        facets = {"author": {}, "pubtype": {}, "category-%s" % lang: {}}

        # Highlighting
        highlighter = Highlighter(SimpleHTMLFormatter('<span class="highlight">', '</span>'), QueryScorer(self.query))

        hitObjects = []
        fields = {}
        for hit in hits:
            doc = searcher.doc(hit.doc)
            # print unicode(doc)
            fields["score"] = hit.score
            fields["volume"] = doc["volume"]
            fields["number"] = doc["number"]
            fields["id"] = doc["id"]
            fields["title"] = doc["title"]
            fields["author"] = doc["author"]
            fields["authors"] = [field.stringValue() for field in doc.getFields("author")]
            for author in fields["authors"]:  # XXX
                facets["author"][author] = facets["author"].get(author, 0) + 1  # XXX

            fields["categories"] = [field.stringValue() for field in doc.getFields("category-%s" % lang)]
            for cat in fields["categories"]:
                facets["category-%s" % lang][cat] = facets["category-%s" % lang].get(cat, 0) + 1
            maxNumFragmentsRequired = 2
            fragmentSeparator = "...";
            pubtype = doc["pubtype"]
            fields["pubtype"] = pubtype
            facets["pubtype"][pubtype] = facets["pubtype"].get(pubtype, 0) + 1
            fields["city"] = doc["city"]
            fields["year"] = doc["year-start"]
            if fields["year"] and doc["year-end"] and doc["year-end"] != fields["year"]:
                fields["year"] += " - " + doc["year-end"]
            highlightFields = ("title", "author", "city", "year", "category")

            if "freetext" in self.criteria:
                for fieldName in highlightFields:
                    try:
                        tokenStream = self.analyzer.tokenStream(fieldName, lucene.StringReader(fields[fieldName]))
                        newVal = highlighter.getBestFragments(tokenStream, fields[fieldName], maxNumFragmentsRequired,
                                                              fragmentSeparator)
                        if len(newVal) > 0:
                            # fields[fieldName] = re.sub(r'</span>\s*<span class="highlight">', ' ', newVal)
                            fields[fieldName] = newVal
                    except:
                        continue

            for fieldName in highlightFields:
                if fieldName in self.criteria or fieldName + "-de" in self.criteria or fieldName + "-en" in self.criteria:
                    try:
                        tokenStream = self.analyzer.tokenStream(fieldName, lucene.StringReader(fields[fieldName]))
                        newVal = highlighter.getBestFragments(tokenStream, fields[fieldName], maxNumFragmentsRequired,
                                                              fragmentSeparator)
                        if len(newVal) > 0:
                            # fields[fieldName] = re.sub(r'</span>\s*<span class="highlight">', ' ', newVal)
                            fields[fieldName] = newVal
                    except:
                        continue
            """if "author" in self.criteria:
                try:
                    tokenStream = self.analyzer.tokenStream("author", lucene.StringReader(fields["author"]))
                    fields["author"] = highlighter.getBestFragments(tokenStream, fields["author"], maxNumFragmentsRequired, fragmentSeparator)
                except:
                        pass"""

            hitObjects.append(
                Hit(fields["id"], fields["volume"], fields["number"], fields["title"], fields["author"], fields["city"],
                    fields["year"], fields["categories"], fields["pubtype"], fields["score"]))

        facetsToDelete = []
        for facet in facets:
            if len(facets[facet]) < 2:
                facetsToDelete.append(facet)
                continue
            values = sorted(facets[facet].items(), key=itemgetter(0))
            values = sorted(values, key=itemgetter(1), reverse=True)
            facets[facet] = values[:25]
        for facet in facetsToDelete:
            del facets[facet]
        self.facets = facets
        reader.close()
        self.hitObjects = hitObjects
        return hitObjects

    def search(self):
        self.createQueryString()
        querystr = self.getQueryString()
        self.query = self.queryParser.parse(querystr)
        return self._getHits()

    def getAll(self):
        self.query = MatchAllDocsQuery()
        return self._getHits()
