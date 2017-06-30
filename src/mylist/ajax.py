from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from mylist.views import to_ris, to_bibtex
from ta_online.search import models# import statement must include ta_online
import settings
from ta_online.settings import Session 
from sqlalchemy.orm import scoped_session, sessionmaker, clear_mappers

@dajaxice_register
def toggleEntry(request, entry_id):
	#NEU, mit POST, redirect zur vorherigen Seite
	mylist = request.session.get('mylist', [])
	if type(entry_id) == type(0):
		if not entry_id in mylist:
			mylist.append(entry_id)
			added = True
		else:
			mylist.remove(entry_id)
			added = False
	request.session['mylist'] = mylist
	return simplejson.dumps({'mylist_count':len(mylist), 'added':added, 'id':entry_id})

@dajaxice_register
def exportEntry(request, exp_format, entry_id):
	#NEU, mit POST, redirect zur vorherigen Seite
	entry = request.db_session.query(models.Entry).filter(models.Entry.id==entry_id).first()

	format_functions = {"ris":to_ris, "bibtex":to_bibtex}
	code = format_functions[exp_format](entry)
	return simplejson.dumps({'export_code':code})

