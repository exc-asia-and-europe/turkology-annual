"""This module contributes LEPL parsers for special parts.

Created on 12.03.2010

@author: dolata, bellm
"""
import re
import lepl
from utils.formattedstring import FormattedString
from utils.parsemethod import parsemethod, rawlist

def TupleApply(matcher, function, raw=False, args=False):
    """With TupleApply you can create more then one named pairs from a
    result."""
    if isinstance(function, tuple):
        function = lambda result, names=function: list([(name, result[0]) for
            name in names if result])
        raw = True
    return lepl.Apply(matcher, function, raw, args)

lepl.Override(apply_=TupleApply,
    space_opt=lambda a, b: lepl.And(a, ~lepl.Space()[0:,...], b)).__enter__()

def Append(input):
    """Appends a value to the parse.""" 
    return lepl.Apply(lepl.Empty(), lambda x:[input], True)

def _transformRoman():
    """Returns a transformer which transforms Roman numerals to integers."""
    m = lepl.Or('M', 'Μ')
    d = lepl.Literal('D')
    c = lepl.Literal('C')
    l = lepl.Literal('L')
    x = lepl.Or('X', 'Χ')
    ix = lepl.Literal('DÍ')
    v = lepl.Or('V', 'v')
    i = lepl.Or('I', 'Ι', 'i', '1', 'Ί', 'Γ', 'l', 'f')
    ii = lepl.Or('H', 'Π')
    iii = lepl.Literal('m')
    return (
        lepl.Substitute(m,    1000) |
        lepl.Substitute(c + m, 900) |
        lepl.Substitute(d,     500) |
        lepl.Substitute(c + d, 400) |
        lepl.Substitute(c,     100) |
        lepl.Substitute(x + c,  90) |
        lepl.Substitute(l,      50) |
        lepl.Substitute(x + l,  40) |
        lepl.Substitute(x,      10) |
        lepl.Substitute(i + x,   9) |
        lepl.Substitute(ix,      9) |
        lepl.Substitute(v,       5) |
        lepl.Substitute(i + v,   4) |
        lepl.Substitute(iii,     3) |
        lepl.Substitute(ii,      2) |
        lepl.Substitute(i,       1))[1:] > sum

roman = _transformRoman()

# Special parsers

def parsePersons(persons):
    """Parses person names."""
    result = rawlist()
    for person in persons.split(' — '):
        person = person.split(', ')
        if person[1:]:
            firstnames = ', '.join(person[1:]).split(' ')
        else:
            firstnames = []
        result.append({'firstnames': firstnames, 'lastname': person[0]})
    result['raw'] = persons
    return result

def parsePersonsReview(persons):
    """Parses person names in a review."""
    result = rawlist()
    for person in persons.split(' — '):
        person = person.split(' ')
        result.append({'firstnames': person[:-1], 'lastname': person[-1]})
    result['raw'] = persons
    return result

def parseCities(cities):
    """Parses city names."""
    result = rawlist(cities.split('-'))
    result['raw'] = cities
    return result

monthDict = {'Januar': 1, 'January': 1,
             'Februar': 2, 'February': 2,
             'März': 3, 'March': 3, 'mars': 3,
             'April': 4,
             'Mai': 5, 'May': 5,
             'Juni': 6, 'June': 6,
             'Juli': 7, 'July': 7,
             'August': 8,
             'September': 9,
             'Oktober': 10, 'October': 10,
             'November': 11,
             'Dezember': 12, 'December': 12}

seasonDict = {'Frühling': 1, 'Spring': 1,
              'Sommer': 2, 'Summer': 2,
              'Herbst': 3, 'Autumn': 3, 'Fall': 3,
              'Winter': 4}

def parseYearRange(range):
    """Parses a year range."""
    strRange = str(range)
    if strRange in monthDict:
        return {'month': monthDict[strRange]}
    elif range in seasonDict:
        return {'season': seasonDict[strRange]}
    return range

def transformYear():
    """Returns a transformer for a year range."""
    year = lepl.Regexp(r'\d{4}') >> int
    yearStart =  year > 'yearStart'
    yearEnd =  year > 'yearEnd'
    yearStartEnd =  year > ('yearStart', 'yearEnd')
    yearBracket = lepl.Or('(', '[') / (year > 'yearBracket') / \
        lepl.Or(')', ']')
    yearAlt = lepl.Literal('/') / year > 'yearAlt'
    range = (lepl.Regexp(r'(?u)[^\W\d]+') >> parseYearRange) > 'range'
    all1 = yearStart / '-' / yearEnd / yearBracket
    all2 = yearStart / '-' / yearEnd / yearAlt
    all3 = yearStart / '-' / yearEnd
    all4 = yearStartEnd / yearBracket
    all5 = yearStartEnd / yearAlt
    all6 = yearStartEnd
    all7 = range / yearStartEnd
    all8 = yearBracket
    return (all1 | all2 | all3 | all4 | all5 | all6 | all7 | all8) > \
        lepl.make_dict

@parsemethod
def parseYear():
    """Parses a year."""
    all = transformYear() / lepl.Eos()
    return all, [
        ('range', parseYearRange)]

def fixPlus(input):
    """Fixes a misrecognized plus sign."""
    input = re.sub('-[a-z0-9]-', '+', input)
    input = re.sub('-[a-z]', '+', input)
    input = re.sub('[a-z0-9]-', '+', input)
    return input

@parsemethod
def parsePaginations():
    """Parses paginations."""
    pagesArabic = lepl.UnsignedInteger() >> int > 'pages'
    pagesRoman = (roman > 'pages') & (Append(True) > 'roman')
    pagesArabicBracket = lepl.Literal('[') / pagesArabic / ']' & \
        (Append(True) > 'bracket')
    pagesRomanBracket = lepl.Literal('[') / pagesRoman / ']' & \
        (Append(True) > 'bracket')

    pages = (pagesArabic | pagesRoman | pagesArabicBracket | \
        pagesRomanBracket) > lepl.make_dict
    pagination = pages / (~lepl.Literal('+') / pages / lepl.Empty())[:] > \
        list
    paginations = pagination / (~lepl.Or(',', ';') / pagination / \
        lepl.Empty())[:] > rawlist
    return paginations, fixPlus

def fixDate(input):
    """Fixes a misrecognized date."""
    input = input.replace(' L', '1.')
    input = input.replace('L', '1')
    return input
    
@parsemethod
def parseDate():
    """Parses a date."""
    day = lepl.Regexp(r'\d{1,2}') >> int
    dayStart = day > 'dayStart'
    dayEnd = day > 'dayEnd'
    dayStartEnd = day > ('dayStart', 'dayEnd')
    month = roman
    monthStart = month > 'monthStart'
    monthEnd = month > 'monthEnd'
    monthStartEnd = month > ('monthStart', 'monthEnd')
    year = lepl.Regexp(r'\d{4}') >> int
    yearStart = year > 'yearStart'
    yearEnd = year > 'yearEnd'
    yearStartEnd = year > ('yearStart', 'yearEnd')

    dot = (lepl.Empty() / '.')[:1]
    problem = Append(True) > 'problem'

    # year, month and day given
    all1 = dayStartEnd & dot / monthStartEnd & dot / yearStartEnd
    all2 = dayStart & dot / '-' / dayEnd & dot / monthStartEnd & dot / \
        yearStartEnd
    all3 = dayStart & dot / monthStart & dot / '-' / dayEnd & dot / \
        monthEnd & dot / yearStartEnd
    all4 = dayStart & dot / monthStart & dot / yearStart / '-' / dayEnd & \
        dot / monthEnd & dot / yearEnd

    # only year and month given
    all5 = monthStartEnd & dot / yearStartEnd
    all6 = monthStart & dot / '-' / monthEnd & dot / yearStartEnd
    all7 = monthStart & dot / yearStart / '-' / monthEnd & dot / yearEnd

    # only year given
    all8 = yearStartEnd
    all9 = yearStart / '-' / yearEnd

    # only day and year given, month forgotten
    all10 = dayStartEnd & dot / yearStartEnd & problem
    all11 = dayStart & dot / '-' / dayEnd & dot / yearStartEnd & problem

    all = (all1 | all2 | all3 | all4 | all5 | all6 | all7 | all8 | all9 |
        all10 | all11) / lepl.Eos() > lepl.make_dict
    return all, fixDate

@parsemethod
def parsePointers():
    """Parses pointers."""
    pointer = lepl.UnsignedInteger() >> int
    pointerStart = pointer > 'pointerStart'
    pointerEnd = pointer > 'pointerEnd'
    pointerStartEnd = pointer > ('pointerStart', 'pointerEnd')
    pointerRange = pointerStart / lepl.Literal('-') / pointerEnd
    pointerDict = pointerStartEnd | pointerRange > lepl.make_dict
    all = pointerDict / (~lepl.Literal(',') / pointerDict / lepl.Empty()
        )[:] / lepl.Eos() > rawlist
    return all

@parsemethod
def parseTAReferences():
    """Parses TA references."""
    volume = (lepl.UnsignedInteger() >> int > 'volume') & (
        lepl.Empty() / '-' / lepl.UnsignedInteger())[:1]
    entry = lepl.UnsignedInteger() >> int > 'entry'
    entryDict = volume / '.' / entry > lepl.make_dict 
    all = ~lepl.Literal('[') / ~lepl.Literal('s.') / ~lepl.Literal('TA') \
        / entryDict & (lepl.Empty() / ~lepl.Or(',', '.') / entryDict)[:] \
        / ~lepl.Literal(']') / lepl.Eos() > rawlist
    return all

def parseNumber(number):
    """Parses a number."""
    try:
        return {'raw': number, 'number': int(number)}
    except ValueError:
        return number

# Reference parsing

def transformTAVolume():
    """Returns a transformer for a TA volume."""
    volume = (lepl.UnsignedInteger() >> int | Append(0)) > 'volume'
    doubleVolume = lepl.UnsignedInteger()
    return volume & (lepl.Empty() / '-' / doubleVolume)[:1] > lepl.make_dict

def transformTAEntry():
    """Returns a transformer for a TA entry."""
    return ((lepl.UnsignedInteger() >> int | Append(0)) > 'entry') > \
        lepl.make_dict

def transformPageReferences():
    """Returns a transformer for page references."""
    pageArabic = lepl.UnsignedInteger() >> int | Append(0)
    pageArabicStart = pageArabic > 'pageStart'
    pageArabicEnd = pageArabic > 'pageEnd'
    pageArabicStartEnd = pageArabic > ('pageStart', 'pageEnd')
    pageArabicRange = pageArabicStart / lepl.Literal('-') / pageArabicEnd

    pageRoman = roman | Append(0)
    pageRomanStart = pageRoman > 'pageStart'
    pageRomanEnd = pageRoman > 'pageEnd'
    pageRomanStartEnd = (pageRoman > ('pageStart', 'pageEnd')) & \
        (Append(True) > 'roman')
    pageRomanRange = (pageRomanStart / lepl.Literal('-') /
        pageRomanEnd) & (Append(True) > 'roman')

    pageStartEnd = pageArabicStartEnd | pageRomanStartEnd
    pageRange = pageArabicRange | pageRomanRange
    pageRangeAsterisk = lepl.Literal('*') / pageRange / '*' & \
        (Append(True) > 'asterisk')

    pageDict = pageStartEnd | pageRange | pageRangeAsterisk > \
        lepl.make_dict
    return pageDict / (~lepl.Or('+', ';', ',') / pageDict / lepl.Empty())[:] \
        > list

def _figuresList(input):
    """Some stuff for the figures."""
    pages = []
    d = [('pages', pages)]
    for page in input:
        if isinstance(page, tuple):
            if page[0] == 'figures':
                d.append(('figures', page[1]))
        else:
            pages.append(page)
    return d

def transformPageReferences(): #@DuplicatedSignature
    """Returns a transformer for page references, too."""
    figures = transformFigureReferences() > 'figures'
    pageArabic = lepl.UnsignedInteger() >> int | Append(0)
    pageArabicStart = pageArabic > 'pageStart'
    pageArabicEnd = pageArabic > 'pageEnd'
    pageArabicStartEnd = pageArabic > ('pageStart', 'pageEnd')
    pageArabicRange = pageArabicStart / lepl.Literal('-') / pageArabicEnd

    pageRoman = roman | Append(0)
    pageRomanStart = pageRoman > 'pageStart'
    pageRomanEnd = pageRoman > 'pageEnd'
    pageRomanStartEnd = (pageRoman > ('pageStart', 'pageEnd')) & \
        (Append(True) > 'roman')
    pageRomanRange = (pageRomanStart / lepl.Literal('-') /
        pageRomanEnd) & (Append(True) > 'roman')

    pageStartEnd = pageArabicStartEnd | pageRomanStartEnd
    pageRange = pageArabicRange | pageRomanRange
    pageRangeAsterisk = lepl.Literal('*') / pageRange / '*' & \
        (Append(True) > 'asterisk')

    pageDict = pageStartEnd | pageRange | pageRangeAsterisk > \
        lepl.make_dict
    result = lepl.Delayed()
    result += pageDict & (lepl.Empty() / ((~lepl.Or(lepl.Literal('.') / ',',
        '.', ',', '+') / figures) | (~lepl.Or('+', ';', ',') / result)))[:1]
    return (result >= _figuresList) & (lepl.Empty() / '.')[:1]
    return pageDict / ((~lepl.Or('+', ';', ',') / pageDict) / lepl.Empty())[:] \
        > list

def transformVolumeReferences():
    """Returns a transformer for volume references."""
    volumeDicts = []
    for volume in [lepl.UnsignedInteger() >> int, roman]:
        volume = volume | Append(0)
        volumeStart = volume > 'volumeStart'
        volumeEnd = volume > 'volumeEnd'
        volumeStartEnd = volume > ('volumeStart', 'volumeEnd')
        volumeRange = volumeStart / lepl.Literal('-') / volumeEnd
        volumeRangeAsterisk = lepl.Literal('*') / volumeRange / '*' & (
            Append(True)> 'asterisk')
        volumeBracket = lepl.Literal('(') / (volume > 'volumeBracket') / ')'
        volumeAlt = lepl.Literal('/') / volume > 'volumeAlt'
        all1 = volumeRange / volumeBracket
        all2 = volumeRange / volumeAlt
        all3 = volumeRange
        all4 = volumeRangeAsterisk / volumeBracket
        all5 = volumeRangeAsterisk / volumeAlt
        all6 = volumeRangeAsterisk
        all7 = volumeStartEnd / volumeBracket
        all8 = volumeStartEnd / volumeAlt
        all9 = volumeStartEnd

        volumeDicts.append(all1 | all2 | all3 | all4 | all5 | all6 | all7 |
            all8 | all9)

    return volumeDicts[0] | volumeDicts[1] & (Append(True) > 'roman') > \
        lepl.make_dict

@parsemethod
def parseVolumes():
    """Parses volume references."""
    return (transformVolumeReferences() / lepl.Eos())

def transformFigureReferences():
    """Returns a transformer for figure references."""
    type1 = lepl.Substitute(lepl.Regexp('Taf(?:eln?)?'), 'plate')
    type2 = lepl.Substitute(lepl.Regexp('Tab'), 'table')
    type3 = lepl.Substitute(lepl.Regexp('Abb'), 'illustration')
    type4 = lepl.Substitute(lepl.Regexp('Karten?'), 'map')
    figureType = ((type1 | type2 | type3 | type4) > 'figureType') & \
        lepl.Or('.', ',')[:1]

    count = (lepl.UnsignedInteger() >> int) | lepl.Substitute('einige', 0)
    counts = ((count & (lepl.Empty() / ~lepl.Literal('+') / count)[:]) >
        list) | Append([1]) > 'counts'
    figureStart = roman > 'figureStart'
    figureEnd = roman > 'figureEnd'
    figureStartEnd = roman > ('figureStart', 'figureEnd')
    figureRange = figureStart / lepl.Literal('-') / figureEnd
    figureRef = (figureStartEnd | figureRange > lepl.make_dict) > 'ref'
    figure = (counts / figureType) | (figureType / figureRef) > \
        lepl.make_dict
    return figure & (lepl.Empty() / ~lepl.Literal(',') / figure)[:] & (
        lepl.Empty() / ~lepl.Literal('.'))[:1] > list

def _makeReference(*parts, yearPos=None):
    """Does some references stuff."""
    result = parts[0]
    for part in parts[1:]:
        result = result / '.' / part
    if yearPos != None: #@UndefinedVariable
        result = result & (Append(yearPos) > 'yearPos') #@UndefinedVariable

    eresult = parts[0]
    for part in parts[1:]:
        eresult = (eresult / '.' / lepl.Empty())[:1] & part

    return result, eresult

def parseReferences(input):
    """Parses references"""
    result = rawlist([_parseReference(item) for item in
        re.split(r'\s*Auch in:?\s*', input)])
    result['raw'] = input
    return result

@parsemethod
def _parseReference():
    """Helper function for parseReferences."""
    ta    = lepl.Or('TA', '7>1', '7/1', '7>t') & (Append(True) > 'ta')
    title = (lepl.Regexp(r'(.*?)\s+(?=\d)') | lepl.Regexp(r'([^\.]+?)\s*(?=\d+\s*(?:-\s*\d+\s*)?\.)')) > 'title'

    taVolume = transformTAVolume() > 'taVolume' 
    taEntry = transformTAEntry() > 'taEntry' 
    year = transformYear() > 'year'
    volume = transformVolumeReferences() > 'volume'
    issue = transformVolumeReferences() > 'issue'
    subIssue = transformVolumeReferences() > 'subIssue'
    pages = transformPageReferences()# > 'pages'

    comment = lepl.Regexp(r'(.*?)\s+(?=\d)') > 'comment'

    ta1 = _makeReference(taVolume, taEntry, pages)
    ta2 = _makeReference(taVolume, taEntry, volume, pages) 

    form1 = _makeReference(year, pages, yearPos=0)
    form2 = _makeReference(year, issue, pages, yearPos=0)
    form3 = _makeReference(volume, year, pages, yearPos=1)
    form4 = _makeReference(volume, year, issue, pages, yearPos=1)
    form5 = _makeReference(volume, year, issue, subIssue, pages, yearPos=1)
    form6 = _makeReference(volume, issue, year, pages, yearPos=2)
    form7 = _makeReference(volume, issue, pages)
    form8 = _makeReference(volume, issue, subIssue, year, pages, yearPos=3)
    #form9 = _makeReference(volume, issue, subIssue, pages)

    taItems = [ta1, ta2]
    items = [form1, form2, form3, form4, form5, form6, form7, form8]
    figures = transformFigureReferences() > 'figures'
    entry = []
    for title, items in [(ta, taItems), (title, items)]:
        references = []
        for item in items:
            #reference = [itemType & dot & (lepl.Empty() /
                #lepl.Or('.', ',', '+') / figures)[:1] for
                #itemType in item]
            reference = list(item)
            reference[0] = reference[0] > lepl.make_dict
            reference[1] = (comment / lepl.Empty())[:1] & reference[1] > lepl.make_dict
            references.append((reference[0] & (lepl.Empty() /
                ~lepl.Or(',', ';') / reference[1])[:] > list) > 'referenceParts')
        entry.append(title / lepl.Or(*references))
    all = (entry[0] | entry[1]) / lepl.Eos() > lepl.make_dict
    return all

class Reference(object):
    """Parser class for a reference.
    """
    referenceRaw = ''
    _referenceRegex = r'(?u)^[\s]*([^\d]*)[\s]*([\d].+)$'
    _referenceMatcher = None
    isTaReference = False
    refTitle = None
    refNumbers = None
    parsedNumbers = {}

    def matchReference(self):
        """Matches a reference."""
        return re.match(self._referenceRegex,
            self.referenceRaw.replace('7>1', 'TA'))

    def parseReferences(self):
        """Parses references."""
        title = self._referenceMatcher.group(1)
        numbers = self._referenceMatcher.group(2)
        title=title.strip()
        if title=='TA':
            self.isTaReference = True
        else:
            self.isTaReference = False
        return title, numbers

    def parseTaReference(self):
        """Parses a TA reference."""
        numbers = [number.strip() for number in self.refNumbers.split('.')]
        if numbers[-1]=='':
            numbers = numbers[:-1]
        if len(numbers)==2:
            self.parsedNumbers['ta-volume'] = self.parseTAVolume(numbers[0])
            self.parsedNumbers['ta-record'] = parseNumber(numbers[1])
        elif len(numbers)==3:
            self.parsedNumbers['ta-volume'] = self.parseTAVolume(numbers[0])
            self.parsedNumbers['ta-record'] = parseNumber(numbers[1])
            self.parsedNumbers['target-pages'] = self.parsePageReferences(
                numbers[2])
        elif len(numbers)==4:
            self.parsedNumbers['ta-volume'] = self.parseTAVolume(numbers[0])
            self.parsedNumbers['ta-record'] = parseNumber(numbers[1])
            self.parsedNumbers['target-volume'] = parseNumber(numbers[2])
            self.parsedNumbers['target-pages'] = self.parsePageReferences(
                numbers[3])
        elif len(numbers)==6 and numbers[3].strip().lower()=='bd' and \
            numbers[4].lower()=='s':
            self.parsedNumbers['ta-volume'] = self.parseTAVolume(numbers[0])
            self.parsedNumbers['ta-record'] = parseNumber(numbers[1])
            self.parsedNumbers['target-volume'] = parseNumber(numbers[2])
            self.parsedNumbers['target-pages'] = self.parsePageReferences(
                numbers[5])
        elif len(numbers)>4:
            self.parsedNumbers['ta-volume'] = self.parseTAVolume(numbers[0])
            self.parsedNumbers['ta-record'] = parseNumber(numbers[1])
            self.parsedNumbers['target-information'] = \
                self.dot.join(numbers[2:])

    def parseArticleReference(self):
        """Parses an article reference."""
        if self.refNumbers!=None:
            numbers = [number.strip() for number in self.refNumbers.split('.')]
            if numbers[-1]=='':
                numbers = numbers[:-1]
            if len(numbers)==2:
                self.parsedNumbers['collection-volume'] = numbers[0]
                self.parsedNumbers['collection-information'] = numbers[1]
            elif len(numbers)==3 and not isinstance(parseYear(numbers[1]),
                str):
                self.parsedNumbers['collection-volume'] = numbers[0]
                self.parsedNumbers['collection-year'] = parseYear(numbers[1])
                self.parsedNumbers['article-pages'] = self.parsePageReferences(
                    numbers[2])
            elif len(numbers)==3:
                self.parsedNumbers['collection-year'] = parseYear(numbers[0])
                self.parsedNumbers['collection-issue'] = numbers[1]
                self.parsedNumbers['article-pages'] = self.parsePageReferences(
                    numbers[2])
                # if there is no volume, year is the volume
            elif len(numbers)==4:
                self.parsedNumbers['collection-volume'] = numbers[0]
                self.parsedNumbers['collection-issue'] = numbers[1]
                self.parsedNumbers['collection-year'] = parseYear(numbers[2])
                self.parsedNumbers['article-pages'] = self.parsePageReferences(
                    numbers[3])
            elif len(numbers)>4:
                self.parsedNumbers['collection-volume'] = numbers[0]
                self.parsedNumbers['collection-year'] = parseYear(numbers[1])
                self.parsedNumbers['article-information'] = \
                    self.dot.join(numbers[2:])

    @staticmethod
    def parseTAVolume(volume):
        """Parses a TA volume number."""
        result = volume.split('-')[0] # First volume at double volumes
        try:
            return {'raw': volume, 'volume': int(result)}
        except ValueError:
            return volume

    @staticmethod
    @parsemethod
    def parsePageReferences():
        """Parses page references."""
        pageArabic = lepl.UnsignedInteger() >> int
        pageArabicStart = pageArabic > 'pageStart'
        pageArabicEnd = pageArabic > 'pageEnd'
        pageArabicStartEnd = pageArabic > ('pageStart', 'pageEnd')
        pageArabicRange = pageArabicStart / lepl.Literal('-') / pageArabicEnd

        pageRoman = roman
        pageRomanStart = pageRoman > 'pageStart'
        pageRomanEnd = pageRoman > 'pageEnd'
        pageRomanStartEnd = (pageRoman > ('pageStart', 'pageEnd')) & \
            (Append(True) > 'roman')
        pageRomanRange = (pageRomanStart / lepl.Literal('-') /
            pageRomanEnd) & (Append(True) > 'roman')

        pageStartEnd = pageArabicStartEnd | pageRomanStartEnd
        pageRange = pageArabicRange | pageRomanRange
        pageRangeAsterisk = lepl.Literal('*') / pageRange / '*' & \
            (Append(True) > 'asterisk')

        pageDict = pageStartEnd | pageRange | pageRangeAsterisk > \
            lepl.make_dict
        all = (pageDict / (~lepl.Or('+',';') / pageDict / lepl.Empty())[:] >
            list) / lepl.Eos()
        return all

    @staticmethod
    @parsemethod
    def parseFigureReferences():
        """Parses figure references."""
        figureName = lepl.Regexp('(Taf(?:eln?)?|Abb|Karten?)[\.,]?') > \
            'figureName'
        count = (lepl.UnsignedInteger() >> int) | lepl.Substitute('einige', 0)
        counts = ((count & (lepl.Empty() / ~lepl.Literal('+') / count)[:]) >
            list) | Append([1]) > 'counts'
        figureStart = roman > 'figureStart'
        figureEnd = roman > 'figureEnd'
        figureStartEnd = roman > ('figureStart', 'figureEnd')
        figureRange = figureStart / lepl.Literal('-') / figureEnd
        figureRef = (figureStartEnd | figureRange > lepl.make_dict) > 'ref'
        figure = (counts / figureName) | (figureName / figureRef) > \
            lepl.make_dict
        all = (figure & (lepl.Empty() / ~lepl.Literal(',') / figure)[:] >
            list) / lepl.Eos()
        return all
    
    def __init__(self, reference):
        """Constructor."""
        try:
            self.parsedNumbers={}
            self.referenceRaw = reference
            if self.matchReference():
                self._referenceMatcher=self.matchReference()
                parsedReference = self.parseReference()
                self.refTitle = parsedReference[0]
                self.refNumbers = parsedReference[1]
                if type(self.refNumbers) == FormattedString:
                    self.dot = FormattedString('.')
                else:
                    self.dot = '.'
            if self.isTaReference:
                self.parseTaReference()
            else:
                self.parseArticleReference()
            self.parsedReference=self.parsedNumbers
            self.parsedReference['is-ta-reference'] = self.isTaReference
            self.parsedReference['title-shortcut'] = self.refTitle
        except:
            print('Exception while processing the following reference: \n' + \
                str(reference))
            raise
