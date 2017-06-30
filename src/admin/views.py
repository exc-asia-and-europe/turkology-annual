from ta_online.search import models
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import sqlalchemy
from django.conf import settings
from django.core.paginator import Paginator
import forms
import re
import os

DB_CONNECTION = 'postgresql://@localhost/ta_db2'


def checkDatabase(request):
    session = models.init(connection=DB_CONNECTION)
    entries = session.query(models.Entry).all()
    for entry in entries:
        if entry.problem == False and (len(entry.title) == 0 or entry.type.__str__() == "unknown"):
            entry.problem = True
    session.commit()


@login_required
def index(request):
    loginForm = forms.LoginForm()
    t = loader.get_template('admin/index.html')
    c = RequestContext(request, {"login_form": loginForm, "db_session": request.db_session})
    return HttpResponse(t.render(c))


"""@login_required
def buildIndex(request):
	if "confirmed" in request.GET:
		buildingProcess = Process(target=buildIndex)
		buildingProcess.start()
"""


@login_required
def editEntry(request, id):
    fields = ["title", "comment", "authors", "cities", "category"]
    sqlalchemy.orm.clear_mappers()
    session = models.init(connection=DB_CONNECTION)
    entry = session.query(models.Entry).filter(models.Entry.id == id).first()
    attributes = []
    for field in fields:
        try:
            attributes.append((field, str(eval("entry." + field))))
        except:
            continue

    t = loader.get_template('admin/edit_entry.html')
    c = RequestContext(request, {'entry': entry, 'attributes': attributes, "entry_object": entry.__str__()})
    return HttpResponse(t.render(c))


def showSuggestions(request):
    pass


@login_required
def showQueryLog(request):
    queries = []
    logFileName = os.path.join(settings.ROOT_DIRECTORY, "search/log/queries.txt")
    if os.path.exists(logFileName):
        logFile = open(logFileName)
        for line in logFile.readlines():
            match = re.search(r"([^\|]+)\|([^\|]+)\|([^\|]+)\|(.*)", line)
            if match:
                queries.append((match.group(1), match.group(2), match.group(3), match.group(4)))
        logFile.close()
    queries.reverse()
    t = loader.get_template('admin/query_log.html')
    c = RequestContext(request, {'queries': queries})
    return HttpResponse(t.render(c))


@login_required
def showObjects(request, className):
    myClass = models.__dict__[className]
    session = request.db_session

    objects = session.query(myClass).yield_per(100)
    attributes = [attr for attr in objects.first().__dict__.keys() if
                  not attr.startswith("_") and not attr.startswith("scanPosition")]
    paginator = Paginator(objects, 100)
    pageNumber = int(request.GET.get("page", 1))
    curPage = paginator.page(pageNumber)
    # Seitenauswahl
    if pageNumber < 4:
        startIndex = 0
    else:
        startIndex = pageNumber - 4
    endIndex = startIndex + 7
    if endIndex > paginator.page_range[-1]:
        offset = endIndex - paginator.page_range[-1]
        startIndex -= offset
        if startIndex < 0:
            startIndex = 0
        endIndex -= offset
    pageRanges = []
    for num in paginator.page_range[startIndex:endIndex]:
        range = "[%d-%d]" % (paginator.page(num).start_index(), paginator.page(num).end_index())
        if num == pageNumber:
            num = None
        pageRanges.append((range, num))
    for obj in curPage.object_list:
        obj.dict = obj.__dict__
    # print obj.dict

    t = loader.get_template('matches.html')
    c = RequestContext(request, {'current_page': curPage, "page_ranges": pageRanges, "class_name": className,
                                 "attributes": attributes, "query": "type:ArticleRepetition"})
    return HttpResponse(t.render(c))


@login_required
def correctionProposals(request):
    pass


def showArticleRepetitions(request):
    session = request.db_session
    articleRepetitions = session.query(models.articleRepetition).all()
    t = loader.get_template('matches.html')
    c = RequestContext(request, {"matches": articleRepetitions})
    return HttpResponse(t.render(c))
