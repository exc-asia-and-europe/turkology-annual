from ta_online.search import models
from django.http import HttpResponse
from django.template import Context, loader, RequestContext
from django.shortcuts import redirect
import re
from django.conf import settings
import os
from datetime import datetime
from ta_online.search.views import showHits
from django.utils.translation import ugettext as _
from django.utils.translation import get_language

def showMyList(request):
	mylist = request.session.get('mylist', [])
	mylist = request.db_session.query(models.Entry).filter(models.Entry.id.in_(mylist)).all()


	language_function = {"de":lambda x:x.nameDE}.get(get_language(), lambda x:x.nameEN)

	for entry in mylist:
		entry.categoryStrings = [language_function(cat) for cat in entry.categories if cat]
		
	title = _("Merkliste")
	categories = []
	sortFields = ("year", "author", "title", "ta")
	activeSortField = "ta"
	ascending = True
	template = "mylist.html"
	return showHits(request, mylist, categories, title, template, sortFields, pagination=False)

"""	t = loader.get_template('mylist.html')
	c = RequestContext(request, {'entries':mylist })

	return HttpResponse(t.render(c))"""




def createBibtex(entry):
	type = entry.type

	if type == "monograph":
		templateFile = open(os.path.join(settings.ROOT_DIRECTORY, "mylist/monograph.bib"))
		template = templateFile.read()
		templateFile.close()
		return template%("%s-%s"%("-".join([a.lastname.lower() for a in entry.authors]),entry.year), " AND ".join([author.__unicode__() for author in entry.authors]), entry.title, "", entry.year)	
	elif type == "article":
		year = None
		refs = entry.references
		if refs and len(refs) > 0:
			for part in refs[0].referenceParts:
				if part.year:
					year = part.year.__unicode__()
					break
		templateFile = open(os.path.join(settings.ROOT_DIRECTORY, "mylist/article.bib"))
		template = templateFile.read()
		templateFile.close()
		return template%("-".join([a.lastname.lower().replace(" ","-") for a in entry.authors]), " AND ".join([author.__unicode__() for author in entry.authors]), entry.title, entry.references[0].title, year or "")
	else:
		return ""

def to_ris(entry, markup=False):
	t = loader.get_template('export/'+entry.type+'.ris')
	c = Context({'entry':entry })
	output =  re.sub(r"\n+", "\n", t.render(c))
	pattern = re.compile(r"^\w+\s*-\s*$\n", re.MULTILINE)
	output = re.sub(pattern, "", output)
	output +="ER - \n"
	if markup:
		pattern = re.compile(r"^(\w\w)", re.MULTILINE)
		output = re.sub(pattern, r"<b>\1</b>", output)
		output = output.replace("\n", "<br/>")
	return output

def to_bibtex(entry, markup=False):
	t = loader.get_template('export/'+entry.type+'.bib')
	c = Context({'entry':entry })
	output =  re.sub(r"\n+", "\n", t.render(c))
	output = output.replace("{ ", "{").replace(" }", "}")
	pattern = re.compile(r"^.*\{\}, *\n", re.MULTILINE)
	output = re.sub(pattern, "", output)
	if markup:
		pattern = re.compile(r"  (\w+) =", re.MULTILINE)
		output = re.sub(pattern, r"  <b>\1</b> = ", output)
		output = output.replace("\n", "<br/>")

	return output





def toggleMyList(request):
	#NEU, mit POST, redirect zur vorherigen Seite
	mylist = request.session.get('mylist', [])
	if request.POST.get("entry_id", None):
		entry_id = int(request.POST["entry_id"])
		if not entry_id in mylist:
			mylist.append(int(entry_id)) 
		else:
			mylist.remove(int(entry_id))
		request.session['mylist'] = mylist
		return redirect(request.POST["next"])
	

def addToMyList(request, entry_id=None):
	mylist = request.session.get('mylist', [])
	#ALT, ohne POST
	if entry_id:
		entry_id = int(entry_id)
		if not entry_id in mylist:
			mylist.append(entry_id)
		request.session['mylist'] = mylist
		return showMyList(request)


def removeFromMyList(request, entry_id):
	entry_id = int(entry_id)
	mylist = request.session.get('mylist', [])
	if entry_id in mylist:
		mylist.remove(entry_id)
	request.session['mylist'] = mylist
	return showMyList(request)

def clearMyList(request):
	request.session['mylist'] = []
	return redirect(showMyList)
	

def save_citation_list(citation_list, file_format):
	output = ""
	format_functions = {"ris":to_ris, "bibtex":to_bibtex}
	file_extensions = {"bibtex":"bib"}
	mime_types = {"ris":"application/x-research-info-systems", "bibtex":"application/x-bibtex"}

	entries = map(format_functions[file_format],citation_list)
	output = "\n".join(entries)

	file_extension = file_extensions.get(file_format,file_format)
	datetime_string = str(datetime.now())[:16].replace(" ", "_").replace(":", "-")

	response = HttpResponse(output, mimetype=mime_types[file_format])
	response['Content-Disposition'] = 'attachment; filename=bibliography_%s.%s'%(datetime_string, file_extension)

	return response

def export_entry(request, entry_id, file_format):
	entry =request.db_session.query(models.Entry).filter(models.Entry.id == entry_id).first()
	return save_citation_list([entry], file_format)
		
def export_list(request, file_format):
	mylist = request.session.get('mylist', [])
	mylist =request.db_session.query(models.Entry).filter(models.Entry.id.in_(mylist))
	return save_citation_list(mylist, file_format)
