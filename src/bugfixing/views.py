# from __future__ import print_function, unicode_literals
from django.template import RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
import forms
import os
import re
from ta_online.search import models
from django.conf import settings
from django.contrib import messages
from ta_online.search import editorModels
from datetime import datetime


def _(foo):
    return foo


def test(request, entry_id):
    if request.POST:
        # firstNamePattern = re.compile(r"author(\d+)-firstname(\d+)")
        lastNamePattern = re.compile(r"author(\d+)-lastname(\d+)")
        authors = {}
        for key, value in request.POST.items():
            if lastNamePattern.search(key):
                num = lastNamePattern.search(key).group(1)
                authors.setdefault(num, {})["last"] = value

        session = request.editor_db_session
        newEntry = editorModels.Monograph(
            request.POST["volume"],
            request.POST["number"],
            [],
            request.POST["title"],
            [],
            "",
            None,
            [],
            request.POST["comment"],
            None,
            [],
            request.POST["raw"],
            request.POST["problem"] == "true",
            int(request.POST["scanPage"]),
            None,
            None,
            [],
            [],
        )
        session.add(newEntry)
        session.commit()
        # print request.user
        mod = editorModels.Modification(entry_id, newEntry.id, datetime.now(), request.user.id)
        session.add(mod)
        session.commit()
        entry = session.query(editorModels.Entry).all()[-1]
        t = loader.get_template('show_entry.html')
        c = RequestContext(request, {'entry': entry})
        return HttpResponse(t.render(c))

    else:
        session = request.db_session
        entry = session.query(models.Entry).filter(models.Entry.id == entry_id).first()
        imageUrl = getScanFileUrl(entry)
        t = loader.get_template('edit_entry.html')
        c = RequestContext(request, {'entry': entry, 'image_url': imageUrl})
        return HttpResponse(t.render(c))


def correct(request, entry_id):
    reload(forms)
    if request.POST:
        messages.add_message(request, messages.INFO, _(
            "Vielen Dank f&uuml;r Ihren Korrekturvorschlag. Er wird so bald wie m&ouml;glich bearbeitet."))
        corrDirName = os.path.join(settings.ROOT_DIRECTORY, "suggestions", entry_id)
        if not os.path.exists(corrDirName):
            os.makedirs(corrDirName)
        corrFileName = os.path.join(corrDirName, request.session.session_key)
        corrFile = open(corrFileName, "w")
        for key, val in request.POST.items():
            corrFile.write("%s:\t" % key)
            corrFile.write(val.encode('utf-8'))
            corrFile.write("\n")
        corrFile.close()
        return HttpResponseRedirect("/show_entry/" + entry_id)
    else:
        entry = request.db_session.query(models.Entry).filter(models.Entry.id == entry_id).first()
        # print entry
        if entry.volume:
            volume = entry.volume
        else:
            volume = ""
        try:
            number = entry.number
        except:
            number = ""
        try:
            title = entry.title
        except:
            title = ""
        try:
            authors = "\n".join(a.__unicode__() for a in entry.authors)
        except:
            authors = ""

        try:
            cities = "\n".join([c.__unicode__() for c in entry.cities])
        except:
            cities = ""
        try:
            year = entry.year
        except:
            year = ""
        try:
            comment = entry.comment
        except:
            comment = ""
        form = forms.GeneralCorrectionForm(initial={
            "volume": volume,
            "number": number,
            "title": title,
            "authors": authors,
            "cities": cities,
            "year": year,
            "comment": comment, })
        imageUrl = getScanFileUrl(entry)
        form.fields["explanation"].label = form.fields["explanation"].label.replace("&amp;", "&")

        t = loader.get_template('correct.html')
        c = RequestContext(request,
                           {'form': form.as_table().replace("&amp;", "&"), 'raw': entry.raw, 'image_url': imageUrl})
        return HttpResponse(t.render(c))


def getScanFileUrl(entry):
    scanFilePattern = re.compile(r"TA%02d_\d{4}_%04d.jpg" % (entry.volume, entry.scanPage))
    scanFileName = ""
    path = os.path.join(settings.ROOT_DIRECTORY, "media/images/scans")
    if os.path.exists(path):
        for fileName in os.listdir(path):
            if scanFilePattern.search(fileName):
                scanFileName = fileName
                break
    imageUrl = "/site_media/images/scans/" + scanFileName
    return imageUrl
