
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



class Node(object):
	def __init__(self, category):
		self.category = category
		self.children = []
		

def resolveCategories(categories):
	categoryLists = []
	if categories == None or len(categories) == 0:
		return None
	for category in categories:
		cur = [category]
		cat = category
		while cat.superCategory != None:
			cur.append(cat.superCategory)
			cat = cat.superCategory
		cur.reverse()
		categoryLists.append(cur)

	root = Node(None)
	if len(categoryLists[0]) > 0:
		root.children.append(makeTree(categoryLists[0][:]))
	del categoryLists[0]

	while len(categoryLists) > 0:
		cur = categoryLists[0][:]
		del categoryLists[0]
		for i in range(len(cur)-1,-1,-1):
			targetNode = findNode(root, cur[i])
			if targetNode != None and targetNode.category != None:
				if len(cur[i+1:]) > 0:
					targetNode.children.append(makeTree(cur[i+1:]))
				break
		else:
			if len(cur) > 0:
				root.children.append(makeTree(cur))
	return prettyPrint(root)
		

def prettyPrint(root):
	if len(root.children) > 0:
		childString = "<ul>%s</ul>"%"\n".join([prettyPrint(child) for child in root.children])
	else:
		childString = ""
	if root.category:
		lang = translation.get_language()
		langString = "en"
		if lang == "de":
			langString = root.category.nameDE
		elif lang == "en":
			langString = root.category.nameEN
		outString = """<li><a href='/%s/browse/categories/%d'>%s%s</a></li>\n"""%(lang, root.category.id, langString, childString)
	else:
		outString = '<div class="categories">%s</div>'%childString 
	return outString

		

		
def findNode(node, category):
	if node.category == category:
		return node
	#if len(node.children) == 0:
	#	return None
	for child in node.children:
		result = findNode(child, category)
		if result != None:
			return result 

def makeTree(categoryList):
	root = Node(categoryList[0])
	previous = root
	i = 2
	for cat in categoryList[1:]:
		i += 2
		cur = Node(cat)
		previous.children.append(cur)
		previous = cur
	return root	

def entry_field(parser, token):
    from re import split
    bits = split(r'\s+', token.contents, 2)
    if len(bits) < 2:
        raise TemplateSyntaxError, "'%s' tag requires two arguments" % bits[0]
    return EntryField(bits[1],bits[2])

register.tag('entry_field', entry_field)
