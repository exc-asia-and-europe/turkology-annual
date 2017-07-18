
#Example usage in html template:
#   <a href="{% addurlparameter sort 1 %}">Sort on field 1</a>
#   <a href="{% addurlparameter output pdf %}">Export as pdf</a>

from django.template import Library, Node, TemplateSyntaxError, Variable
from django.utils import translation
from django.utils.translation import ugettext as _


register = Library()

class EntryField(Node):
    def __init__(self, fieldName, fieldValue):
        self.fieldName = fieldName.strip("'").strip('"')
        self.fieldValue = Variable(fieldValue) 

    def render(self, context):
	LANG = context["LANGUAGE_CODE"]

	try:
		val = self.fieldValue.resolve(context)
	except:
		val = "" 

	try:
		if len(val) == 0:
			val = None 
	except:
		pass
	if str(type(val)) == "<class 'sqlalchemy.ext.associationproxy._AssociationList'>":
		if self.fieldName == "Artikel":
			articles = sorted([(art.id, unicode(art.title), ", ".join([unicode(author) for author in art.authors])) for art in val], key=lambda art: unicode(art[1]))
			articleStrings = ['<li><a href="/%s/show_entry/%d">%s <span class="authors">%s</span></a></li>'%(LANG, art[0], art[1], art[2]) for art in articles]
			val = "<ul>%s</ul>"%("\n".join(articleStrings))

		elif self.fieldName == "In":
			try:
				val = '<a href="/%s/show_entry/%d">%s</a>'%(LANG, val[0].id, unicode(val[0].title))
			except AttributeError:
				val = '<a href="/%s/show_entry/%d">%s</a>'%(LANG, val[0].id, unicode(val[0].raw))
		else:
			val = ", ".join([v.__unicode__() for v in val])

	fieldNames = {u"Band":_("Band"), "Titel":_("Titel"),"Nummer":_("Nummer"), "Kommentare":_("Kommentare"), "Rezensionen":_("Rezensionen"), "Berichte": _("Berichte"), "Typ":_("Typ"), "Ort":_("Ort"), "Jahr":_("Jahr"), "Schlagworte":_("Schlagworte"), "Datum":_("Datum"), "Artikel":_("Artikel"), "Seiten":_("Seiten")}

	if self.fieldName == "Seiten" and val:
		val = ", ".join([unicode(v) for v in val])

	if self.fieldName == "Schlagworte":
		val = resolveCategories(val)

	if (val == None):
		className = ' class="empty"'
	else:
		className = ''
        return '<tr%s><th>%s:</th><td>%s</td></tr>' % (className, fieldNames.get(self.fieldName, self.fieldName), repr(self.fieldName, val))


def repr(fieldName, fieldValue):
	if fieldName == "Typ":
		fieldValue = {"article":_("Artikel"), "collection": _("Sammelband"), "monograph": _("Monographie"), "conference": _("Konferenzbericht")}.get(fieldValue,fieldValue)
	return fieldValue




def bibtex_id(parser, token):
    from re import split
    bits = split(r'\s+', token.contents, 2)
    if len(bits) < 2:
        raise TemplateSyntaxError, "'%s' tag requires two arguments" % bits[0]
    return EntryField(bits[1],bits[2])

register.tag('bibtex_id', bibtex_id)
