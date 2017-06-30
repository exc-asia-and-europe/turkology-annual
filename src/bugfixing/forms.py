# -*- coding:utf-8 -*-
from django.utils.translation import ugettext as _
from django import forms


class GeneralCorrectionForm(forms.Form):
    # volume = forms.CharField()
    title = forms.CharField(widget=forms.Textarea(), label=_("Titel"))
    authors = forms.CharField(widget=forms.Textarea(), label=_("Autoren"),
                              help_text="(" + _("Ein Autor pro Zeile") + ")")
    cities = forms.CharField(widget=forms.Textarea(), label=_("Orte"), help_text="(%s)" % _("Ein Ort pro Zeile"))
    year = forms.CharField(label=_("Jahr"))
    explanation = forms.CharField(widget=forms.Textarea(), label=_("Erl&auml;uterung"),
                                  help_text=_("Bitte erl&auml;utern Sie gegebenenfalls Ihren Vorschlag."))
