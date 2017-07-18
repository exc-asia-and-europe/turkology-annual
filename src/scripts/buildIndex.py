from lucene import *
import os
from ta_online.search import models, analyzers
from ta_online.search.models import Entry
import sys
import time
from datetime import timedelta
from ta_online import settings

PROGRESS_STEP = 500


def buildIndex(num=None):
    initVM()

    session = settings.getSession()
    if not num:
        entries = session.query(Entry).yield_per(1000)  # .filter(Entry.volume==volume)
    else:
        entries = session.query(Entry).yield_per(1000).limit(num)  # .filter(Entry.volume==volume)

    analyzer = analyzers.PorterStemmerAnalyzer()

    # analyzer = StandardAnalyzer(lucene.Version.LUCENE_30)
    indexDir = settings.LUCENE_INDEX_DIRECTORY
    lockFileName = os.path.join(indexDir, "write.lock")

    # if os.path.exists(lockFileName):
    #	raise RuntimeError("The index is currently locked. Check whether it is being processed at the moment, otherwise delete 'building.lock'.")
    directory = MMapDirectory(File(indexDir))
    writer = IndexWriter(directory, analyzer, True, IndexWriter.MaxFieldLength.LIMITED)
    writer.deleteAll()

    cur = 0
    print "Starting to build index.."

    try:
        if sys.argv[1] == "--test":
            entries = entries[:100]
    except:
        pass
    total = entries.count()
    logFile = open("buildIndex.log", "w")
    for entry in entries:
        cur += 1
        if entry.problem or str(entry.type).endswith("Repetition") or str(entry.type) == "bullet":
            continue

        doc = Document()

        catchall = []

        # ID
        doc.add(Field("id", str(entry.id), Field.Store.YES, Field.Index.NOT_ANALYZED))

        # Titel
        try:
            title = unicode(entry.title)
            doc.add(
                Field("title", title, Field.Store.YES, Field.Index.ANALYZED, Field.TermVector.WITH_POSITIONS_OFFSETS))
            doc.add(Field("title-normalized", title, Field.Store.NO, Field.Index.ANALYZED))
            doc.add(Field("title-sort", title, Field.Store.NO, Field.Index.NOT_ANALYZED))
            catchall.append(title)
        except AttributeError:
            continue

        # Autoren
        try:
            for author in entry.authors:
                author = unicode(author)
                doc.add(Field("author", author, Field.Store.YES, Field.Index.ANALYZED,
                              Field.TermVector.WITH_POSITIONS_OFFSETS))
                doc.add(Field("author-sort", author, Field.Store.YES, Field.Index.NOT_ANALYZED))
                catchall.append(author)

        except AttributeError:
            logFile.write("Entry %d does not have attribute 'authors'\n" % entry.id)

        # Zeitschrift
        try:
            journal = entry.references[0].title.lower()
            doc.add(Field("journal", journal, Field.Store.YES, Field.Index.NOT_ANALYZED))
            catchall.append(journal)
        except IndexError:
            pass
        except AttributeError:
            pass

        # Orte
        try:
            for city in entry.cities:
                city = unicode(city)
                doc.add(Field("city", city, Field.Store.YES, Field.Index.NOT_ANALYZED))
                doc.add(Field("city-sort", city, Field.Store.NO, Field.Index.NOT_ANALYZED))
                catchall.append(city)
        except AttributeError:
            logFile.write("Entry %d does not have attribute 'cities'\n" % entry.id)

        # Jahr

        if entry.type == "conference":
            try:
                startYear = entry.date.startYear
                if startYear:
                    doc.add(Field("year-start", str(startYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                    catchall.append(str(startYear))
            except:
                pass
            try:
                endYear = entry.date.endYear
                if endYear:
                    doc.add(Field("year-end", str(endYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                    catchall.append(str(endYear))
            except:
                pass

        # Artikel in ...
        elif entry.type == "article":
            if len(entry.collections) > 0:
                superEntry = entry.collections[0]
                # ... Konferenzbericht
                if superEntry.type == "conference":
                    try:
                        startYear = superEntry.date.startYear
                        endYear = superEntry.date.endYear
                        if startYear:
                            doc.add(Field("year-start", str(startYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                            catchall.append(str(startYear))
                    except:
                        pass
                    try:
                        if endYear:
                            doc.add(Field("year-end", str(endYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                            catchall.append(str(endYear))

                    except:
                        pass
                # ... Sammelband
                else:  # if superEntry.type == "collection":
                    try:
                        startYear = superEntry.year.start
                        if startYear:
                            doc.add(Field("year-start", str(startYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                            catchall.append(str(startYear))
                    except:
                        pass
                    try:
                        endYear = superEntry.year.end
                        if endYear:
                            doc.add(Field("year-end", str(endYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                            catchall.append(str(endYear))
                    except:
                        pass
            # ... Zeitschrift
            else:
                try:
                    startYear = entry.references[0].referenceParts[0].year.start
                    if startYear:
                        doc.add(Field("year-start", str(startYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                        catchall.append(str(startYear))

                except:
                    pass
                try:
                    endYear = entry.references[0].referenceParts[0].year.end
                    if endYear:
                        doc.add(Field("year-end", str(endYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                        catchall.append(str(endYear))
                except:
                    pass
        else:
            try:
                startYear = entry.year.start
                if startYear:
                    doc.add(Field("year-start", str(startYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                    catchall.append(str(startYear))
            except:
                pass
            try:
                endYear = entry.year.start
                if endYear:
                    doc.add(Field("year-end", str(endYear), Field.Store.YES, Field.Index.NOT_ANALYZED))
                    catchall.append(str(endYear))
            except:
                pass

        # Schlagwort
        # try:
        for category in entry.getCategories():
            if category == None:
                continue
            doc.add(Field("category-de", category.nameDE, Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("category-en", category.nameEN, Field.Store.YES, Field.Index.ANALYZED))
            doc.add(Field("category-label", category.label, Field.Store.NO, Field.Index.ANALYZED))
            # doc.add(Field("category-sort", catName, Field.Store.NO, Field.Index.NOT_ANALYZED))
            catchall.append(category.nameDE)
            catchall.append(category.nameEN)

        # except AttributeError:
        #	logFile.write("Entry %d does not have attribute 'category'\n"%entry.id)

        # Band
        try:
            doc.add(Field("volume", str(entry.volume), Field.Store.YES, Field.Index.NOT_ANALYZED))
        except AttributeError:
            logFile.write("Entry %d does not have attribute 'volume'\n" % entry.id)

        # Typ
        try:
            doc.add(Field("pubtype", str(entry.type), Field.Store.YES, Field.Index.NOT_ANALYZED))
        except AttributeError:
            pass
        # Eintragsnummer
        try:
            if entry.number != None:
                doc.add(Field("number", str(entry.number), Field.Store.YES, Field.Index.NOT_ANALYZED))
        except AttributeError:
            logFile.write("Entry %d does not have attribute 'number'\n" % entry.id)

        # Catch-All-Feld
        try:

            freetext = Field("freetext", " ".join(catchall), Field.Store.YES, Field.Index.ANALYZED)
            freetextNormalized = Field("freetext-normalized", " ".join(catchall), Field.Store.YES, Field.Index.ANALYZED)
            # freetext.setBoost(10.0)
            # freetextNormalized.setBoost(0.1)
            doc.add(freetext)
            doc.add(freetextNormalized)
        except AttributeError:
            logFile.write("Entry %d does not have attribute 'raw'\n" % entry.id)

        # writer.updateDocument(Term("id", str(entry.id)), doc)
        writer.addDocument(doc)
        if cur % PROGRESS_STEP == 0 or cur == 1:
            sys.stdout.write("%d von %d\n" % (cur, total))
        # if cur > 1000:
        #	break
    writer.optimize()
    writer.close()


# logFile.close()
if __name__ == "__main__":
    if len(sys.argv) > 1:
        buildIndex(int(sys.argv[1]))
    else:
        buildIndex()
