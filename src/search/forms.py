from django.utils.translation import ugettext as _
from django import forms
from django.utils.translation import get_language

rawFields = [
    ("freetext", _("Freitext"), True, False),
    ("relevance", _("Relevanz"), False, True),
    ("title", _("Titel"), True, True),
    ("author", _("Autor"), True, True),
    # ("city",     _("Ort"),        True,         True),
    ("year", _("Jahr"), True, True),
    ("volume", _("TA Band"), True, True),
    ("ta", _("TA"), False, True),
    ("journal", _("Zeitschrift"), True, True),
]

if get_language() == "de":
    rawFields.append(("category-de", _("Schlagwort"), True, True))
else:
    rawFields.append(("category-en", _("Schlagwort"), True, True))

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


fields = [Field(field[0], field[1], field[2], field[3]) for field in rawFields]


class SimpleSearchForm(forms.Form):  # search form for a simple search
    query = forms.CharField(label=_("Suchbegriff"))
    hitsperpage = forms.ChoiceField(label=_("Treffer pro Seite"),
                                    choices=(("10", 10), ("15", 15), ("20", 20), ("50", 50)))
    orderby = forms.ChoiceField(label=_("Sortierung"),
                                choices=[(field.name, field.repr) for field in fields if field.sortable])
    # order = forms.ChoiceField(label=_("Reihenfolge"), choices = [("asc", _("aufsteigend")), ("desc", _("absteigend"))], widget = forms.widgets.RadioSelect)


class AdvancedSearchForm(forms.Form):  # search form for a simple search
    searchCriteria = [(field.name, field.repr) for field in fields if field.searchable]
    query1 = forms.CharField()
    query2 = forms.CharField()
    query3 = forms.CharField()
    criterion1 = forms.ChoiceField(choices=searchCriteria, widget=forms.Select(attrs={'class': 'criterion'}))
    criterion2 = forms.ChoiceField(choices=searchCriteria, widget=forms.Select(attrs={'class': 'criterion'}))
    criterion3 = forms.ChoiceField(choices=searchCriteria, widget=forms.Select(attrs={'class': 'criterion'}))
    conjunction1 = forms.ChoiceField(choices=conjunctions, widget=forms.Select(attrs={'class': 'conjunction'}))
    conjunction2 = forms.ChoiceField(choices=conjunctions, widget=forms.Select(attrs={'class': 'conjunction'}))
    orderby = forms.ChoiceField(label=_("Sortierung"),
                                choices=[(field.name, field.repr) for field in fields if field.sortable])
    hitsperpage = forms.ChoiceField(label=_("Treffer pro Seite"),
                                    choices=(("10", 10), ("15", 15), ("20", 20), ("50", 50)))
