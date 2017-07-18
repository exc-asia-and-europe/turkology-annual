"""
This module includes the LineParserTa class for the 19th volume of Turkology Annual.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""

import lepl
from utils import specialparser
from utils.parsemethod import parsemethod
from lineparsers.lineparsertabase import LineParserTaBase

class LineParserTa(LineParserTaBase):

    @staticmethod
    @parsemethod
    def matchMonographWCountry():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?,)') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=,)') > 'cities'
        country = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4},)') > 'country'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        pages = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'pages'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / country / ',' / year / ',' / pages / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchArticle():
        """
        This function matches and parses line including record
        representing an article.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParserTa.matchArticle('923.Altun, Kudret     '
        ... 'XX. yüzyúlda divan óiiri geleneõini sürdüren Kayserili '
        ... 'óáir Halim Kámi Teoman. In: TK 433.1999.296-302. [Ein '
        ... 'Bewahrer der Diwandichtungstradition im 20. Jh. – Halim '
        ... 'Kámi Teoman aus Kayseri.]'))
        {'authors': [{'firstnames': ['Kudret'], 'lastname': 'Altun'},
                     raw='Altun, Kudret'],
         'comment': '[Ein Bewahrer der Diwandichtungstradition im 20.
             Jh. – Halim Kámi Teoman aus Kayseri.]',
         'number': {'number': 923, 'raw': '923'},
         'raw': '923.Altun, Kudret     XX. yüzyúlda divan óiiri
             geleneõini sürdüren Kayserili óáir Halim Kámi Teoman. In:
             TK 433.1999.296-302. [Ein Bewahrer der
             Diwandichtungstradition im 20. Jh. – Halim Kámi Teoman aus
             Kayseri.]',
         'references': [{'raw': 'TK 433.1999.296-302.',
                         'referenceParts':
                             [{'pages': [{'pageEnd': 302,
                                          'pageStart': 296}],
                               'volume': {'volumeEnd': 433,
                                          'volumeStart': 433},
                               'year': {'yearEnd': 1999,
                                        'yearStart': 1999},
                               'yearPos': 1}],
                         'title': 'TK'},
                        raw='TK 433.1999.296-302.'],
         'title': 'XX. yüzyúlda divan óiiri geleneõini sürdüren
             Kayserili óáir Halim Kámi Teoman.'}
        >>> pprint(LineParserTa.matchArticle("2711.Yedúyildiz, "
        ... "Bahaeddin — Acun, Fatma     Únternet'te vakúflar. In: "
        ... "VD 26.1997.5-24."))
        {'authors': [{'firstnames': ['Bahaeddin'],
                      'lastname': 'Yedúyildiz'},
                     {'firstnames': ['Fatma'], 'lastname': 'Acun'},
                     raw='Yedúyildiz, Bahaeddin — Acun, Fatma'],
         'number': {'number': 2711, 'raw': '2711'},
         'raw': "2711.Yedúyildiz, Bahaeddin — Acun, Fatma
             Únternet'te vakúflar. In: VD 26.1997.5-24.",
         'references': [{'raw': 'VD 26.1997.5-24.',
                         'referenceParts':
                             [{'pages': [{'pageEnd': 24,
                                          'pageStart': 5}],
                               'volume': {'volumeEnd': 26,
                                          'volumeStart': 26},
                               'year': {'yearEnd': 1997,
                                        'yearStart': 1997},
                               'yearPos': 1}],
                         'title': 'VD'},
                        raw='VD 26.1997.5-24.'],
         'title': "Únternet'te vakúflar."}
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchConference():
        """
        This function matches and parses line including record
        representing a conference.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParserTa.matchConference("284.    Ankara, "
        ... "10.-12.XII.1998: ￢ﾀﾜBilanￃﾧo 1923-1998: Tￃﾼrkiye "
        ... "Cumhuriyeti'nin 75 yￃﾺlￃﾺna toplu bakￃﾺￃﾳ￢ﾀﾝ Uluslararasￃﾺ "
        ... "Kongresi / Inter-national Conference on ￢ﾀﾜHistory of "
        ... "the Turkish Republic: A re-assessment￢ﾀﾝ."))
        {'cities': ['Ankara', raw='Ankara'],
         'date': {'dayEnd': 12,
                  'dayStart': 10,
                  'monthEnd': 12,
                  'monthStart': 12,
                  'raw': '10.-12.XII.1998',
                  'yearEnd': 1998,
                  'yearStart': 1998},
         'number': {'number': 284, 'raw': '284'},
         'raw': "284.    Ankara, 10.-12.XII.1998: ￢ﾀﾜBilanￃﾧo 1923-1998:
             Tￃﾼrkiye Cumhuriyeti'nin 75 yￃﾺlￃﾺna toplu bakￃﾺￃﾳ￢ﾀﾝ
             Uluslararasￃﾺ Kongresi / Inter-national Conference on
             ￢ﾀﾜHistory of the Turkish Republic: A re-assessment￢ﾀﾝ.",
         'title': "￢ﾀﾜBilanￃﾧo 1923-1998: Tￃﾼrkiye Cumhuriyeti'nin 75
             yￃﾺlￃﾺna toplu bakￃﾺￃﾳ￢ﾀﾝ Uluslararasￃﾺ Kongresi /
             Inter-national Conference on ￢ﾀﾜHistory of the Turkish
             Republic: A re-assessment￢ﾀﾝ."}
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        date = lepl.Regexp(r'(?u)(.*?)(?=: )') > 'date'
        title = lepl.Regexp(r'(?u)(.*)') > 'title' 
        comment = lepl.Regexp(r'(?u)(\[.*\])')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / cities / ',' / date / ':' / title / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchArticleRepetition():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=\[)') > 'title'
        references = lepl.Regexp(r'(?u)(\[s\.[\s]{0,1}TA .*\]|\[S\.[\s]{0,1}TA .*\])(?=\.)') > 'references'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / references / comment / '.' / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseTAReferences)]

    def getMatchers(self):
        return [
            (self.matchConferenceWCountryWComment, 'conference', True),
            (self.matchConferenceWCountry, 'conference', True),
            (self.matchConferenceWComment, 'conference', True),
            (self.matchConference, 'conference', True),
            (self.matchMasterThesisWCity, 'monographMasterthesis', False),
            (self.matchMasterThesisWoCity, 'monographMasterthesis', False),
            (self.matchDissertationWCity, 'monographDissertation', False),
            (self.matchDissertationWoCity, 'monographDissertation', False),
            (self.matchMonographWCountry, 'monograph', False),
            (self.matchMonograph, 'monograph', False),
            (self.matchArticle, 'article', False),
            (self.matchCollectionWEditorWVolume, 'collection', False),
            (self.matchCollectionWCountryWEditor, 'collection', False),
            (self.matchCollectionWEditor, 'collection', False),
            (self.matchCollectionWVolume, 'collection', False),
            (self.matchCollection, 'collection', False),
            (self.matchArticleRepetition, 'articleRepetition', False),
            (self.matchCollectionRepetition, 'collectionRepetition', False)]

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
