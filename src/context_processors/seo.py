from django.utils.translation import get_language
from re import sub
from django.utils.http import urlencode


def otherLanguages(request):
    try:
        allLanguages = ["de", "en"]
        currentLang = get_language()
        allLanguages.remove(currentLang)
        currentUrlParts = request.META["PATH_INFO"].split("/")
        getString = removeParams(request.GET.copy(), {u"sess": None})
        otherLanguages = []
        for lang in allLanguages:
            otherUrl = "/".join(["http://kjc-fs2.kjc.uni-heidelberg.de:8000", lang] + currentUrlParts[2:]) + getString
            otherLanguages.append((lang, otherUrl))
        return {"OTHER_LANGUAGES": otherLanguages}
    except:
        return {}


def canonicalUrl(request):
    baseUrl = "http://kjc-fs2.kjc.uni-heidelberg.de:8000" + request.META["PATH_INFO"]
    subUrl = removeParams(request.GET.copy(),
                          {u"sess": None, u"page": u"1", u"order": u"asc", u"hitsperpage": u"20", u"orderby": u"ta"})
    return {"CANONICAL_URL": baseUrl + subUrl}


def removeParams(getDict, params):
    for key, val in params.items():
        if val is None:
            try:
                getDict.pop(key)
            except KeyError:
                pass
        else:
            if key in getDict and val == getDict[key]:
                getDict.pop(key)
    if len(getDict) > 0:
        url = "?"
    else:
        url = ""
    return url + getDict.urlencode()
