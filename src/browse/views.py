from django.http import HttpResponse
from django.template import loader, RequestContext
from django.utils.translation import ugettext as _
import ta_online.search.models as models
from django.conf import settings
from ta_online.hitlist.models import Category
from ta_online.search.views import showHits
from ta_online.search.TASearcher import TASearcher
from django.utils.translation import get_language


def browseTa(request):
    # Aktuelle Band-Nr.
    currentNumber = int(request.GET.get("category", 1))

    categories = [Category(i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
                                        18, 19, 20, 21, 22, 24, 25, 26]]
    for cat in categories:
        if cat.name == currentNumber:
            cat.active = True
    orderby = [request.GET.get("orderby", "ta")]
    order = request.GET.get("order", "asc")
    if order == "desc":
        ascending = False
    else:
        ascending = True

    if not "ta" in orderby:
        orderby.append("ta")

    searcher = TASearcher(queries=[str(currentNumber)], criteria=["volume"], orderby=orderby, ascending=ascending)
    hits = searcher.search()

    sortFields = ("ta", "title", "author", "year")

    return showHits(request, hits, categories, "%s: %s %d" % (_("Bl&auml;ttern"), _("Band"), currentNumber),
                    "browse/browse_base.html", sortFields, orderby[0], ascending, {"preface": currentNumber})


def browseCategories(request, categoryId=None):
    session = request.db_session
    # Kategorienuebersicht
    if not categoryId:

        categories = sorted(session.query(models.Category).all(), key=lambda c: c.label)
        t = loader.get_template('browse/category_list.html')
        c = RequestContext(request, {"categories": categories, "language": get_language()})
        return HttpResponse(t.render(c))
    else:
        category = session.query(models.Category).get(int(categoryId))
        superCategories = [category]
        cur = category
        while cur.superCategory != None:
            superCategories.append(cur.superCategory)
            cur = cur.superCategory
        superCategories.reverse()

        categoryNames = []
        lastCategoryName = ""
        for cat in superCategories:
            if get_language() == "de":
                categoryName = cat.nameDE
                LANG = "de"
            else:
                categoryName = cat.nameEN
                LANG = "en"
            categoryNames.append('<a href="/%s/browse/categories/%d">%s</a>' % (LANG, cat.id, categoryName))
            lastCategoryName = categoryName

        orderby = [request.GET.get("orderby", "ta")]
        order = request.GET.get("order", "asc")
        if order == "desc":
            ascending = False
        else:
            ascending = True

        sortFields = ("ta", "title", "author", "year")

        searcher = TASearcher(queries=[category.label + "*"], criteria=["category-label"], orderby=orderby,
                              ascending=ascending)
        hits = searcher.search()
        title = "%s: %s (%d)" % (_("Bl&auml;ttern"), lastCategoryName, len(hits))
        context = {"category_tree": categoryNames}
        return showHits(request, hits, [], title, "browse/browse_categories.html", sortFields, orderby[0], ascending,
                        context=context)


def browseJournals(request):
    """session = settings.getSession()
    volumeNumbers = range(1, 27)
    volumeNumbers.remove(23)
    mylist = request.session.get("mylist", [])

    #GET-Optionen
    currentNumber = int(request.GET.get("category", 1))
    pageNumber = int(request.GET.get("page", 1))


    categories = [Category(i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
            18, 19, 20, 21, 22, 24, 25, 26]]
    for cat in categories:
        if cat.name == currentNumber:
            cat.active = True

    entries = session.query(models.Entry).filter(models.Entry.volume == currentNumber).order_by('number')

    hitsPerPage=50
    paginator = Paginator(entries, hitsPerPage)
    currentPage = paginator.page(pageNumber)

    # Seitenauswahl
    if pageNumber < 4:
        startIndex = 0
    else:
        startIndex = pageNumber - 4
    endIndex = startIndex + 7
    if endIndex > paginator.page_range[-1]:
        offset = endIndex - paginator.page_range[-1]
        startIndex -= offset
        if startIndex <0:
            startIndex = 0
        endIndex -= offset
    pageRanges = []
    for num in paginator.page_range[startIndex:endIndex]:
        pageRange = "%d-%d"%(paginator.page(num).start_index(), paginator.page(num).end_index())
        if num == pageNumber:
            num = None
        pageRanges.append((pageRange, num))
    #/Seitenauswahl
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
                searches[searchKey] = request.META["PATH_INFO"] + "?" + request.META["QUERY_STRING"] + "&sess=%d"%searchKey
        request.session["searches"] = searches



    t = loader.get_template('browse/browse_ta.html')
    c = RequestContext(request, {"categories":categories, "current_page":currentPage, "page_ranges":pageRanges, "mylist":mylist, "search_key":searchKey})
    return HttpResponse(t.render(c))"""
