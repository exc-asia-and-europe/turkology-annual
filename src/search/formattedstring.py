from __future__ import print_function, unicode_literals
from xml.sax import ContentHandler, parseString
from xml.sax.saxutils import escape
import sys

if sys.version_info[0] == 2:
    str = unicode  # @UndefinedVariable
    bytes = lambda string, encoding: str(string)

id2name = {'0436': 'Afrikaans', '041C': 'Albanian', '0401': 'Arabic', '1401': 'Arabic Algeria',
           '3C01': 'Arabic Bahrain', '0C01': 'Arabic Egypt', '0801': 'Arabic Iraq', '2C01': 'Arabic Jordan',
           '3401': 'Arabic Kuwait', '3001': 'Arabic Lebanon', '1001': 'Arabic Libya', '1801': 'Arabic Morocco',
           '2001': 'Arabic Oman', '4001': 'Arabic Qatar', '0401': 'Arabic Saudi Arabia', '2801': 'Arabic Syria',
           '1C01': 'Arabic Tunisia', '3801': 'Arabic U.A.E', '2401': 'Arabic Yemen', '042B': 'Armenian',
           '044D': 'Assamese', '082C': 'Azeri Cyrillic', '042C': 'Azeri Latin', '042D': 'Basque',
           '0813': 'Belgian Dutch', '080C': 'Belgian French', '0445': 'Bengali', '0416': 'Portuguese (Brazil)',
           '0402': 'Bulgarian', '0455': 'Burmese', '0423': 'Byelorussian (Belarusian)', '0403': 'Catalan',
           '0C04': 'Chinese Hong Kong SAR', '1404': 'Chinese Macau SAR', '0804': 'Chinese Simplified',
           '1004': 'Chinese Singapore', '0404': 'Chinese Traditional', '041A': 'Croatian', '0405': 'Czech',
           '0406': 'Danish', '0413': 'Dutch', '0C09': 'English Australia', '2809': 'English Belize',
           '1009': 'English Canadian', '2409': 'English Caribbean', '1813': 'English Ireland',
           '2009': 'English Jamaica', '1409': 'English New Zealand', '3409': 'English Philippines',
           '1C09': 'English South Africa', '2C09': 'English Trinidad', '0809': 'English U.K.', '0409': 'English U.S.',
           '3009': 'English Zimbabwe', '0425': 'Estonian', '0438': 'Faeroese', '0429': 'Farsi', '040B': 'Finnish',
           '040C': 'French', '2C0C': 'French Cameroon', '0C0C': 'French Canadian', '300C': "French Cote d'Ivoire",
           '140C': 'French Luxembourg', '340C': 'French Mali', '180C': 'French Monaco', '200C': 'French Reunion',
           '280C': 'French Senegal', '1C0C': 'French West Indies', '240C': 'French Congo (DRC)',
           '0462': 'Frisian Netherlands', '083C': 'Gaelic Ireland', '043C': 'Gaelic Scotland', '0456': 'Galician',
           '0437': 'Georgian', '0407': 'German', '0C07': 'German Austria', '1407': 'German Liechtenstein',
           '1007': 'German Luxembourg', '0408': 'Greek', '0447': 'Gujarati', '040D': 'Hebrew', '0439': 'Hindi',
           '040E': 'Hungarian', '040F': 'Icelandic', '0421': 'Indonesian', '0410': 'Italian', '0411': 'Japanese',
           '044B': 'Kannada', '0460': 'Kashmiri', '043F': 'Kazakh', '0453': 'Khmer', '0440': 'Kirghiz',
           '0457': 'Konkani', '0412': 'Korean', '0454': 'Lao', '0426': 'Latvian', '0427': 'Lithuanian',
           '042F': 'FYRO Macedonian', '044C': 'Malayalam', '083E': 'Malay Brunei Darussalam', '043E': 'Malaysian',
           '043A': 'Maltese', '0458': 'Manipuri', '044E': 'Marathi', '0450': 'Mongolian', '0461': 'Nepali',
           '0414': 'Norwegian Bokmol', '0814': 'Norwegian Nynorsk', '0448': 'Oriya', '0415': 'Polish',
           '0816': 'Portuguese', '0446': 'Punjabi', '0417': 'Rhaeto-Romanic', '0418': 'Romanian',
           '0818': 'Romanian Moldova', '0419': 'Russian', '0819': 'Russian Moldova', '043B': 'Sami Lappish',
           '044F': 'Sanskrit', '0C1A': 'Serbian Cyrillic', '081A': 'Serbian Latin', '0430': 'Sesotho', '0459': 'Sindhi',
           '041B': 'Slovak', '0424': 'Slovenian', '042E': 'Sorbian', '040A': 'Spanish (Traditional)',
           '2C0A': 'Spanish Argentina', '400A': 'Spanish Bolivia', '340A': 'Spanish Chile', '240A': 'Spanish Colombia',
           '140A': 'Spanish Costa Rica', '1C0A': 'Spanish Dominican Republic', '300A': 'Spanish Ecuador',
           '440A': 'Spanish El Salvador', '100A': 'Spanish Guatemala', '480A': 'Spanish Honduras',
           '4C0A': 'Spanish Nicaragua', '180A': 'Spanish Panama', '3C0A': 'Spanish Paraguay', '280A': 'Spanish Peru',
           '500A': 'Spanish Puerto Rico', '0C0A': 'Spanish Spain (Modern Sort)', '380A': 'Spanish Uruguay',
           '200A': 'Spanish Venezuela', '0430': 'Sutu', '0441': 'Swahili', '041D': 'Swedish', '081D': 'Swedish Finland',
           '100C': 'Swiss French', '0807': 'Swiss German', '0810': 'Swiss Italian', '0428': 'Tajik', '0449': 'Tamil',
           '0444': 'Tatar', '044A': 'Telugu', '041E': 'Thai', '0451': 'Tibetan', '0431': 'Tsonga', '0432': 'Tswana',
           '041F': 'Turkish', '0442': 'Turkmen', '0422': 'Ukrainian', '0420': 'Urdu', '0843': 'Uzbek Cyrillic',
           '0443': 'Uzbek Latin', '0433': 'Venda', '042A': 'Vietnamese', '0452': 'Welsh', '0434': 'Xhosa',
           '0435': 'Zulu'}


class FormattedString(str):
    def __new__(cls, word, lang=None):
        result = super(FormattedString, cls).__new__(cls, word)
        result.lang = [lang] * len(word)
        return result

    def __add__(self, other):
        result = super(FormattedString, self).__new__(FormattedString,
                                                      super(FormattedString, self).__add__(other))
        if type(other) == FormattedString:
            result.lang = self.lang + other.lang
        else:
            result.lang = self.lang + [None] * len(other)
        return result

    def __radd__(self, other):
        result = super().__new__(FormattedString,
                                 super(FormattedString, self).__add__(other))
        if type(other) == FormattedString:
            result.lang = self.lang + other.lang
        else:
            result.lang = [None] * len(other) + self.lang
        return result

    def __getitem__(self, index):
        result = super(FormattedString, self).__new__(FormattedString,
                                                      super(FormattedString, self).__getitem__(index))
        if type(index) == slice:
            result.lang = self.lang[index]
        else:
            result.lang = [self.lang[index]]
        return result

    def __repr__(self):
        return 'f' + repr(self.beautify())

    def lstrip(self):
        for i, c in enumerate(self):
            if not c.isspace():
                return self[i:]
        return FormattedString('')

    def rstrip(self):
        for i, c in enumerate(reversed(self)):
            if not c.isspace():
                return self[:len(self) - i]
        return FormattedString('')

    def strip(self):
        for i, c in enumerate(self):
            if not c.isspace():
                for j, c in enumerate(reversed(self)):
                    if not c.isspace():
                        return self[i:len(self) - j]
        return FormattedString('')

    def split(self, sep=None):
        if not sep:
            return self._splitWhitespace()
        elif len(sep) == 1:
            return self._splitChar(sep)
        else:
            return self._splitSubstring(sep)

    def _splitWhitespace(self):
        result = []
        pos = 0
        for i, char in enumerate(self):
            if char.isspace():
                part = self[pos:i]
                if part: result.append(part)
                pos = i + 1
        part = self[pos:]
        if part: result.append(part)
        return result

    def _splitChar(self, sep):
        result = []
        pos = 0
        for i, char in enumerate(self):
            if char == sep:
                part = self[pos:i]
                result.append(part)
                pos = i + 1
        part = self[pos:]
        result.append(part)
        return result

    def _splitSubstring(self, sep):
        result = []
        length = len(sep)
        oldpos = 0
        pos = self.find(sep)
        while pos != -1:
            result.append(self[oldpos:pos])
            pos += length
            oldpos = pos
            pos = self.find(sep, pos)
        result.append(self[oldpos:])
        return result

    def splitlines(self):
        result = []
        pos = 0
        e = enumerate(self)
        for i, char in e:
            if char == '\n' or char == '\r':
                part = self[pos:i]
                result.append(part)
                if char == '\r' and i + 1 < len(self) and self[i + 1] == '\n':
                    next(e)
                    pos = i + 2
                else:
                    pos = i + 1
        part = self[pos:]
        if part: result.append(part)
        return result

    def join(self, sequence):
        lst = list(sequence)
        if not lst: return FormattedString('')
        result = super(FormattedString, self).__new__(FormattedString,
                                                      super(FormattedString, self).join(lst))
        result.lang = self._getLangList(lst[0])
        for item in lst[1:]:
            result.lang.extend(self.lang)
            result.lang.extend(self._getLangList(item))
        return result

    @staticmethod
    def _getLangList(str):
        if hasattr(str, 'lang'):
            return str.lang
        return [None] * len(str)

    def replace(self, old, new, count=-1):
        string = str(self)
        lang = self.lang[:]
        pos = string.find(old)
        i = 0
        while pos != -1 and (count == -1 or i < count):
            string = string[:pos] + new + string[pos + len(old):]
            lang[pos:pos + len(old)] = [lang[pos]] * len(new)
            pos = string.find(old, pos + len(new))
            i += 1
        result = super(FormattedString, self).__new__(FormattedString, string)
        result.lang = lang
        return result

    def setLang(self, lang, start, end):
        for i in range(start, end):
            self.lang[i] = lang

    def getLang(self, start=0, end=2147483647):
        result = self.lang[start:end]
        if len(set(result)) == 1 and result[0]:
            return result[0]

    def beautify(self):
        result = []
        oldlang = None
        for char, lang in zip(self, self.lang):
            if lang != oldlang:
                if lang:
                    name = id2name.get(lang, lang)
                else:
                    name = ''
                result.append('[[%s]]' % name)
            result.append(char)
            oldlang = lang
        return ''.join(result)

    def toXml(self):
        result = []
        oldlang = None
        for char, lang in zip(self, self.lang):
            if lang != oldlang:
                if oldlang: result.append('</lang>')
                if lang: result.append('<lang id="%s">' % lang)
            result.append(escape(char))
            oldlang = lang
        if oldlang: result.append('</lang>')
        return ''.join(result)

    @staticmethod
    def parse(xml):
        handler = FormattedStringHandler()
        parseString(b'<?xml version="1.0"?><doc>' + bytes(xml,
                                                          encoding='utf8') + b'</doc>', handler)
        return handler.result


class FormattedStringHandler(ContentHandler):
    def __init__(self):
        self.lang = []
        self.result = FormattedString('')

    def startElement(self, name, attrs):
        self.attrs = attrs
        if name == 'lang':
            self.lang.append(attrs.get('id'))

    def endElement(self, name):
        if name == 'lang':
            self.lang.pop()

    def characters(self, data):
        lang = None
        if self.lang:
            lang = self.lang[-1]
        self.result += FormattedString(data, lang)
