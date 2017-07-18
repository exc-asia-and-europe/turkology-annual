# -*- coding:utf-8 -*-

from django import forms


class GeneralCorrectionForm(forms.Form):
    # volume = forms.CharField()
    title = forms.CharField(widget=forms.Textarea(), label="Titel")
    authors = forms.CharField(widget=forms.Textarea(), label="Autoren", help_text="(Ein Autor pro Zeile)")
    cities = forms.CharField(widget=forms.Textarea(), label="Orte", help_text="(Ein Ort pro Zeile)")
    year = forms.CharField(label="Jahr")
    explanation = forms.CharField(widget=forms.Textarea(), label="Erlaeuterung",
                                  help_text="Bitte erl&auml;utern Sie gegebenenfalls Ihren Vorschlag.")


class PersonForm(forms.Form):
    def __init__(self, *args, **kwargs):
        person = args[0]
        args = args[1:]
        print
        person
        super(PersonForm, self).__init__(*args, **kwargs)

        self.fields['lastname'] = forms.CharField(label="Nachname", initial=person.lastname)
        i = 1
        for firstname in person.firstnames:
            self.fields['firstName%d' % i] = forms.CharField(label="%d. Vorname" % i, initial=firstname)
            i += 1
