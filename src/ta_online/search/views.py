import codecs
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.template import loader, RequestContext
from django.utils.translation import ugettext as _
import forms
import models
import re
import TASearcher
from ta_online.hitlist.models import Category
from django.utils.html import escape
from django.utils.translation import get_language
import sys


def showHits(request, hits, categories, title, template, sortFields, activeSortField=None, ascending=None, context={},
             facets={}, filters=[], pagination=True):
    reload(forms)
    # Benutzer-Optionen: wenn nicht gesetzt, default
    pageNumber = int(request.GET.get("page", 1))
    hitsPerPage = int(request.GET.get("hitsperpage", 20))
    if not pagination:
        hitsPerPage = len(hits)
        if hitsPerPage == 0:
            hitsPerPage += 1
        pageNumber = 1

    paginator = Paginator(hits, hitsPerPage)
    currentPage = paginator.page(pageNumber)
    # Seitenauswahl
    if pageNumber < 4:
        startIndex = 0
    else:
        startIndex = pageNumber - 4
    endIndex = startIndex + 12
    if endIndex > paginator.page_range[-1]:
        offset = endIndex - paginator.page_range[-1]
        startIndex -= offset
        if startIndex < 0:
            startIndex = 0
        endIndex -= offset
    pageRanges = []
    for num in paginator.page_range[startIndex:endIndex]:
        range = "%d-%d" % (paginator.page(num).start_index(), paginator.page(num).end_index())
        if num == pageNumber:
            num = None
        pageRanges.append((range, num))

    # Sorting

    if activeSortField == None:
        activeSortField = [request.GET.get("orderby", "ta")]
    if ascending == None:
        order = request.GET.get("order", "asc")
        ascending = (order == "asc")

    sortFields = [(field[0], field[1]) for field in forms.rawFields if field[-1] and field[0] in sortFields]

    # Suchsession-Handling

    searches = request.session.get("searches", {})
    if request.GET.get("sess", None):
        searchKey = int(request.GET["sess"])
        searches[searchKey] = request.META["PATH_INFO"] + "?" + request.META["QUERY_STRING"]
    else:
        existingNums = searches.keys()
        if len(searches) > 0:
            searchKey = max(existingNums) + 1
        else:
            searchKey = 0
        searches[searchKey] = request.META["PATH_INFO"] + "?" + request.META["QUERY_STRING"] + "&sess=%d" % searchKey
    request.session["searches"] = searches

    hitlists = request.session.get("hitlists", {})
    hitlist = [hit.id for hit in hits]
    hitlists[searchKey] = hitlist
    request.session["hitlists"] = hitlists
    if request.META.get("IS_CRAWLER", False):
        request.session.clear()

    # Pagination


    mylist = request.session.get('mylist', [])
    totalMatches = len(hits)

    # hitlist: Entry-IDs der gefundenen Eintraege
    request.session["hitlist"] = []
    for hit in hits:
        request.session["hitlist"].append(hit.id)

    t = loader.get_template(template)
    finalContext = {"current_page": currentPage,
                    "total_matches": totalMatches, "page_ranges": pageRanges,
                    "mylist": mylist,
                    "categories": categories,
                    'sort_fields': sortFields,
                    'search_key': searchKey,
                    'title': title,
                    'hits_per_page': hitsPerPage,
                    'page_sizes': [20, 50, 100, 200],
                    'order_by': activeSortField,
                    'ascending': ascending,
                    'facets': facets,
                    }
    for key, val in context.items():
        finalContext[key] = val
    c = RequestContext(request, finalContext)
    return HttpResponse(t.render(c))


def removeBrackets(query):
    return query.replace("(", " ").replace(")", " ")


def search(request, advanced=False):
    reload(forms)
    if not request.GET and not advanced:
        return home(request)
        """form = forms.SimpleSearchForm()
        t = loader.get_template('simple.html')
        c = RequestContext(request, {'form':form })
        return HttpResponse(t.render(c))"""
    elif advanced:
        form = forms.AdvancedSearchForm()
        t = loader.get_template('advanced.html')
        c = RequestContext(request, {'form': form})
        return HttpResponse(t.render(c))
    if "query" in request.GET:  # simple search
        queries = [removeBrackets(request.GET["query"])]
        criteria = ["freetext"]
        conjunctions = []
    elif "query1" in request.GET:  # advanced search
        queries = [removeBrackets(request.GET.get("query%d" % i, "")) for i in xrange(1, 4)]
        criteria = [request.GET.get("criterion%d" % i, "") for i in xrange(1, 4)]
        conjunctions = [request.GET.get("conjunction%d" % i, "") for i in xrange(1, 3)]
    filtersNum = len([param for param in request.GET if param.startswith("filter_name")])
    filters = []
    for num in range(1, filtersNum + 1):
        filterName = request.GET["filter_name%d" % num]
        filterValue = request.GET["filter_value%d" % num]
        queries.append('"%s"' % filterValue)
        # if filterName == "author":
        #	criteria.append(filterName+"-sort")
        # else:
        criteria.append(filterName)
        conjunctions.append("AND")
        filters.append("%s: %s" % (filterName, filterValue))
    orderby = [request.GET.get("orderby", "ta")]
    order = request.GET.get("order", "asc")
    if order == "desc":
        ascending = False
    else:
        ascending = True

    # try:
    searcher = TASearcher.TASearcher(queries, criteria, conjunctions, orderby=orderby, ascending=ascending)
    hits = searcher.search()
    facets = searcher.facets
    """#except Exception, e:
        sys.stdout.write(str(e) + "\n")
        hits = []
        facets = []"""
    hitSelection = []
    pubtypeTranslations = (
        ("all", _("Alle")),
        ("article", _("Artikel")),
        ("conference", _("Konferenzberichte")),
        ("monograph", _("Monographien")),
        ("collection", _("Sammelb&auml;nde")),
    )
    pubtypeDistribution = {}
    for hit in hits:
        hitType = hit.pubtype
        pubtypeDistribution[hitType] = pubtypeDistribution.get(hitType, 0) + 1
    pubtypeDistribution["all"] = sum(pubtypeDistribution.values())
    pubtypes = [Category(type, repr=prettyType, count=pubtypeDistribution[type]) for type, prettyType in
                pubtypeTranslations if type in pubtypeDistribution.keys()]
    curPubtype = request.GET.get("category", "all")
    if curPubtype != "all":
        for hit in hits:
            if hit.pubtype == curPubtype:
                hitSelection.append(hit)
    else:
        hitSelection = hits[:]
    for pub in pubtypes:
        if pub.name == curPubtype:
            pub.active = True
            break

    # clean up query workaround for normalized search
    query = re.sub(r' *OR [\w-]+-normalized:.*', r"", searcher.getQueryString())
    query = query.replace("freetext:", "")
    query = query.replace("+", " ")
    query = query.strip("()")

    """
    #Query-Logging
    if not request.user.is_authenticated():
        logFile = codecs.open(os.path.join(settings.ROOT_DIRECTORY, "search/log/queries.txt"), "a", "utf-8")
        session_key = request.session.session_key
        ip = request.META["REMOTE_ADDR"] #request.META['HTTP_X_FORWARDED_FOR']
        logFile.write("%s|%s|%s|%s\n"%(str(datetime.now())[:16], session_key, query, ip))
        logFile.close()
    """
    sortFields = ("year", "author", "title", "ta")

    return showHits(request, hitSelection, pubtypes, "%d %s: '%s'" % (len(hits), _("Treffer f&uuml;r"), escape(query)),
                    "search/matches.html", sortFields, orderby[0], ascending, facets=facets, filters=filters)


def advancedSearch(request):
    return search(request, advanced=True)


@login_required
def showProblemEntries(request):
    session = request.db_session
    entries = session.query(models.Entry).filter(models.Entry.problem == True).all()
    for entry in entries:
        try:
            if len(entry.references) > 1:
                pass  # print entry
        except:
            continue
    t = loader.get_template('problems.html')
    c = RequestContext(request, {"entries": entries})
    return HttpResponse(t.render(c))


def showEntry(request, *args):
    """Displays the detailed entry page"""
    mylist = request.session.get('mylist', [])
    session = request.db_session
    if len(args) == 1:
        entry = session.query(models.Entry).filter(models.Entry.id == args[0]).first()
    elif len(args) == 2:
        entry = session.query(models.Entry).filter(models.Entry.volume == args[0]).filter(
            models.Entry.number == args[1]).first()

    if str(entry.type) == "article" and len(entry.references) > 0:
        referenceString = models.formatReferences(entry.references).replace("..", ".").replace("..", ".")
        ref = entry.references[0]
        if ref.type == "ta":
            url = '<a href="/show_entry/%d/%d">%s</a>' % (
                ref.referenceParts[0].taVolume, ref.referenceParts[0].taEntry, referenceString)
        elif ref.type == "article":
            url = '<a href="/?query1=%s&criterion1=journal">%s</a>' % (ref.title, referenceString)
        entry.referenceString = url
    t = loader.get_template('show_entry.html')

    # Back to results page
    searchKey = -1
    backLink = None
    if request.GET.get("sess", None):
        searchKey = request.GET["sess"]
        if searchKey.isdigit() and int(searchKey) in request.session.get("searches", {}):
            backLink = request.session["searches"].get(int(searchKey))

    # previous and next hit
    previous = None
    next = None

    hitlists = request.session.get("hitlists", {})
    hitlist = hitlists.get(int(searchKey), [])
    idx = 0
    if entry.id in hitlist:
        idx = hitlist.index(entry.id)
        prevIdx = idx - 1
        nextIdx = idx + 1
        if prevIdx >= 0:
            previous = hitlist[prevIdx]
        if nextIdx < len(hitlist):
            next = hitlist[nextIdx]
    request.session["hitlists"] = hitlists

    c = RequestContext(request, {'entry': entry, "entry_object": "entry.__str__()", "previous": previous, "next": next,
                                 "mylist": mylist, "total_hits": len(hitlist), "hit_number": idx + 1,
                                 "back_link": backLink, "search_key": searchKey})
    return HttpResponse(t.render(c))


def getIds(searchResults):
    ids = [match.doc for match in searchResults]
    return ids


def about(request):
    t = loader.get_template('about.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


def prefaces(request):
    volumes = range(1, 22) + ["22-23"] + range(24, 27)
    volumes = [str(vol) for vol in volumes]
    t = loader.get_template('prefaces.html')
    c = RequestContext(request, {"volumes": volumes})
    return HttpResponse(t.render(c))


def showPreface(request, volume):
    t = loader.get_template('prefaces/%s' % volume)
    c = RequestContext(request)  # , { })
    # return HttpResponse(open("/home/dustin/work/eclipse/ta_online/media/prefaces/TA%s.htm"%volume).read())

    return HttpResponse(t.render(c))


def home(request):
    if get_language() == "de":
        languageCode = "de"
    else:
        languageCode = "en"
    t = loader.get_template('home/home_%s.html' % languageCode)
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


def robotsTxt(request):
    return HttpResponse("""User-agent: *
Disallow: /de/report_error/
Disallow: /de/admin/
Disallow: /de/mylist/

Disallow: /en/report_error/
Disallow: /en/admin/
Disallow: /en/mylist/
""", mimetype="text/plain")


def showPlainTextEntry(request, entry_id):
    session = request.db_session
    entry = session.query(models.Entry).get(entry_id)

    fields = ["authors", "title", "number", "cities", "year", "comment", "references", "paginations", "type"]
    transDict = {"authors": "author", "cities": "city", "yearStart": "year", "references": "reference",
                 "paginations": "pages"}
    output = []
    try:
        editors = entry.editors
        editorTokens = []
        for editor in editors:
            editorTokens.append(" ".join(map(unicode, editor.firstnames)))
            editorTokens.append(unicode(editor.lastname))
        output.append("%s\t%s" % ("editor", " ".join(editorTokens)))
    except:
        pass

    for field in fields:
        resValue = u""
        try:
            value = eval("entry." + field)
            if not value:
                continue
            if "_AssociationList" in str(type(value)) or "OrderingList" in str(type(value)):
                for part in value:
                    resValue += unicode(part)
            else:
                resValue = unicode(value)
            output.append(u"%s\t%s" % (transDict.get(field, field), resValue))
        except Exception as inst:
            pass
    return HttpResponse(u"\n".join(output), mimetype="text/plain; charset=utf-8")
