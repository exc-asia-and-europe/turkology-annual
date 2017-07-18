"""
This module includes the LineParser class.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""

import lepl
import re
from utils import specialparser
from utils.constantandconfig import LineParserTa, RANGE_CONFERENCE
from utils.debug import Logger
from utils.parsemethod import parsemethod, rawlist

class LineParser(object):
    """
    This class is for parsing separate lines included in the Turkology Annual.
    As a line we take the whole record with its own individual number as
    well as annotations beginning with a bullet or another special marking
    (e.g. Rez., Bericht, Referate).
    """

    @staticmethod
    @parsemethod
    def matchCategory():
        """
        This function matches and parses line including category and
        returns a list containing dictionary with parsed category.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchCategory('AE. Museen'))
        {'catLabel': 'AE', 'catName': 'Museen', 'raw': 'AE. Museen'}
        """
        catLabel = lepl.Regexp(r'(?u)([A-Z]{1,5})(?=\.)') > 'catLabel'
        catName = lepl.Regexp(r'(?u)(.*)') > 'catName'
        all = lepl.Empty() / catLabel / '.' / catName / lepl.Eos() > \
            lepl.make_dict
        return all

    @staticmethod
    @parsemethod
    def matchMonograph():
        """
        This function matches and parses line including record
        representing a monograph.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchMonograph('815.Yelten, '
        ... 'Muhammet     Nev’îzáde Atáyî. Sohbetü’l-ebkár. Ústanbul, '
        ... '1999, XXXII+288 S. [Sohbetü’l-ebkár von Nev’îzáde Atáyî '
        ... '(1583-1635).]'))
        {'authors': [{'firstnames': ['Muhammet'], 'lastname': 'Yelten'},
                     raw='Yelten, Muhammet'],
         'cities': ['Ústanbul', raw='Ústanbul'],
         'comment': '[Sohbetü’l-ebkár von Nev’îzáde Atáyî
             (1583-1635).]',
         'number': {'number': 815, 'raw': '815'},
         'paginations': [[{'pages': 32, 'roman': True}, {'pages': 288}],
                         raw='XXXII+288'],
         'raw': '815.Yelten, Muhammet     Nev’îzáde Atáyî.
             Sohbetü’l-ebkár. Ústanbul, 1999, XXXII+288 S.
             [Sohbetü’l-ebkár von Nev’îzáde Atáyî (1583-1635).]',
         'title': 'Nev’îzáde Atáyî. Sohbetü’l-ebkár.',
         'year': {'raw': '1999', 'yearEnd': 1999, 'yearStart': 1999}}
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?, ' \
            '[\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4},)') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)([^\n]*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / \
            ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > \
            lepl.make_dict
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
        >>> pprint(LineParser.matchArticle('923.Altun, Kudret     XX. '
        ... 'yüzyúlda divan óiiri geleneõini sürdüren Kayserili óáir '
        ... 'Halim Kámi Teoman. In: TK 433.1999.296-302. [Ein Bewahrer '
        ... 'der Diwandichtungstradition im 20. Jh. – Halim Kámi '
        ... 'Teoman aus Kayseri.]'))
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
        >>> pprint(LineParser.matchArticle("2711.Yedúyildiz, Bahaeddin "
        ... "— Acun, Fatma     Únternet'te vakúflar. In: "
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
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / \
            references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchCollection():
        """
        This function matches and parses line including record
        representing collection.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchCollection('3291.Croisades et '
        ... 'pélèrinages. Récits, chroniques et voyages en Terre '
        ... 'sainte, XIIe–XVIIe siècle. Danielle Régnier-Bohler ed. '
        ... 'Paris, 1997, LXXI+ 1438 S.'))
        {'cities': ['Paris', raw='Paris'],
         'comment': '',
         'number': {'number': 3291, 'raw': '3291'},
         'paginations': [[{'pages': 71, 'roman': True},
                          {'pages': 1438}],
                         raw='LXXI+ 1438'],
         'raw': '3291.Croisades et pélèrinages. Récits, chroniques et
             voyages en Terre sainte, XIIe–XVIIe siècle. Danielle
             Régnier-Bohler ed. Paris, 1997, LXXI+ 1438 S.',
         'title': 'Croisades et pélèrinages. Récits, chroniques et
             voyages en Terre sainte, XIIe–XVIIe siècle. Danielle
             Régnier-Bohler ed.',
         'year': {'raw': '1997', 'yearEnd': 1997, 'yearStart': 1997}}
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?, ' \
            '[\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4},)') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / cities / ',' / year / ',' \
            / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchConference():
        """
        This function matches and parses line including record
        representing a conference.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchConference("284.    Ankara, "
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
        date = lepl.Regexp(r'(?u)(\d.*?)(?=: )') > 'date'
        title = lepl.Regexp(r'(?u)([^\[^]*)') > 'title'
        comment = lepl.Regexp(r'(?u)(\[.*\])')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / cities / ',' / date / ':' / \
            title / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchReferate():
        """
        This function matches and parses line including 'Referate' at
        the beginning.

        >>> from pprint import pprint
        >>> pprint(LineParser.matchReferate('Referate: Writing in the '
        ... 'Altaic world. Juha Janhunen — Volker Rybatzki ed. '
        ... 'Helsinki, 1999, 326 S. (Studia Orientalia, 87).'))
        {'cities': ['. Helsinki', raw='. Helsinki'],
         'comment': '(Studia Orientalia, 87).',
         'paginations': [[{'pages': 326}], raw='326'],
         'raw': 'Referate: Writing in the Altaic world. Juha Janhunen —
             Volker Rybatzki ed. Helsinki, 1999, 326 S. (Studia
             Orientalia, 87).',
         'referate': 'Referate',
         'title': 'Writing in the Altaic world. Juha Janhunen — Volker
             Rybatzki ed',
         'year': {'raw': '1999', 'yearEnd': 1999, 'yearStart': 1999}}
        """
        referate = lepl.Regexp(r'(?u)(Referate)(?=: )') > 'referate'
        title = lepl.Regexp(r'(?u)(.*?)(?=. [^\d^\.^:\,]*?, [\d]{4}, '
            r'[\d]{1,5} S.)') > 'title'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / referate / ':' / title / cities / ',' / year / \
            ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchReferateWEditor():
        """
        This function matches and parses line including 'Referate' at
        the beginning and the information on the editor (marked by '.ed' following a name).

        >>> from pprint import pprint
        >>> pprint(LineParser.matchReferate('Referate: Writing in the '
        ... 'Altaic world. Juha Janhunen — Volker Rybatzki ed. '
        ... 'Helsinki, 1999, 326 S. (Studia Orientalia, 87).'))
        {'cities': ['. Helsinki', raw='. Helsinki'],
         'comment': '(Studia Orientalia, 87).',
         'paginations': [[{'pages': 326}], raw='326'],
         'raw': 'Referate: Writing in the Altaic world. Juha Janhunen —
             Volker Rybatzki ed. Helsinki, 1999, 326 S. (Studia
             Orientalia, 87).',
         'referate': 'Referate',
         'title': 'Writing in the Altaic world. ',
         'editors': 'Juha Janhunen — Volker Rybatzki', 
         'year': {'raw': '1999', 'yearEnd': 1999, 'yearStart': 1999}}
        """
        referate = lepl.Regexp(r'(?u)(Referate)(?=: )') > 'referate'
        title = lepl.Regexp(r'(?u)(?:.*?\.)+(?=.*ed\s*\.)') > 'title'
        editors = lepl.Regexp(r'(?u)(.*?)\s*(?=ed\s*.)') > 'editors'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / referate / ':' / title / editors / 'ed' / '.' / \
            cities / ',' / year / ',' / paginations / 'S.' / comment / \
            lepl.Eos() > lepl.make_dict
        return all, [
            ('editors', specialparser.parsePersonsReview),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchReferateWoTitleWEditor():
        """
        This function matches and parses line including 'Referate' at
        the beginning and the information on the editor (marked by '.ed' following a name), 
        but without the information on the title.


        """
        referate = lepl.Regexp(r'(?u)(Referate)(?=: )') > 'referate'
        editors = lepl.Regexp(r'(?u)((?:(?:^|\s+)\S{1,2}\.|[^\.])*?)\s*'
            '(?=ed\s*.)') > 'editors' # forbid dots but not in initials
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / referate / ':' / editors / 'ed' /' .' / \
            cities / ',' / year / ',' / paginations / 'S.' / comment / \
            lepl.Eos() > lepl.make_dict
        return all, [
            ('editors', specialparser.parsePersonsReview),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchReferateWoTitle():
        """
        This function matches and parses line including 'Referate' at
        the beginning, but without the information on the referat's title.
        """
        referate = lepl.Regexp(r'(?u)(Referate)(?=: )') > 'referate'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / referate / ':' / cities / ',' / year / ',' / \
            paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchReferateWoTitleWoPaginations():
        """
        This function matches and parses line including 'Referate' at
        the beginning, but without the information on pages.
        """
        referate = lepl.Regexp(r'(?u)(Referate)(?=: )') > 'referate'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / referate / ':' / cities / ',' / year / ',' / \
            comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchReport():
        """
        This function matches and parses line starting with "Bericht"
        and including the name(s) of the author(s).

        >>> from pprint import pprint
        >>> pprint(LineParser.matchReport('Bericht: Gábor HAUSNER, '
        ... 'HK 112.4.1999.892-894.'))
        {'authors': [{'firstnames': [], 'lastname': 'Gábor HAUSNER'},
                     raw='Gábor HAUSNER'],
         'raw': 'Bericht: Gábor HAUSNER, HK 112.4.1999.892-894.',
         'references': [{'raw': 'HK 112.4.1999.892-894.',
                         'referenceParts':
                             [{'issue': {'volumeEnd': 4,
                                         'volumeStart': 4},
                               'pages': [{'pageEnd': 894,
                                          'pageStart': 892}],
                               'volume': {'volumeEnd': 112,
                                          'volumeStart': 112},
                               'year': {'yearEnd': 1999,
                                        'yearStart': 1999},
                               'yearPos': 2}],
                         'title': 'HK'},
                        raw='HK 112.4.1999.892-894.'],
         'report': 'Bericht'}
        """
        report = lepl.Regexp(r'(?u)(Bericht)(?=: )') > 'report'
        authors = lepl.Regexp(r'(?u).*(?=, )') > 'authors'
        references = lepl.Regexp(r'(?u)[\s]*([^\d]*[\s]*[\d].+)') > \
            'references'
        all = lepl.Empty() / report / ':' / authors / ',' / references > \
            lepl.make_dict
        return all, [
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchReportWoAuthors():
        """
        This function matches and parses line starting with "Bericht"
        but not including the name of the author.

        >>> from pprint import pprint
        >>> pprint(LineParser.matchReportWoAuthors('Bericht: '
        ... 'HK 112.4.1999.892-894.'))
        {'raw': 'Bericht: HK 112.4.1999.892-894.',
         'references': [{'raw': 'HK 112.4.1999.892-894.',
                         'referenceParts':
                             [{'issue': {'volumeEnd': 4,
                                         'volumeStart': 4},
                               'pages': [{'pageEnd': 894,
                                          'pageStart': 892}],
                               'volume': {'volumeEnd': 112,
                                          'volumeStart': 112},
                               'year': {'yearEnd': 1999,
                                        'yearStart': 1999},
                               'yearPos': 2}],
                         'title': 'HK'},
                        raw='HK 112.4.1999.892-894.'],
         'report': 'Bericht'}
        """
        report = lepl.Regexp(r'(?u)(Bericht)(?=: )') > 'report'
        references = lepl.Regexp(r'(?u)[\s]*([^\d]*[\s]*[\d].+)') > \
            'references'
        all = lepl.Empty() / report / ':' / references > lepl.make_dict
        return all, [
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchAnyRecord():
        """
        This function matches and parses line composed of any number at
        the beginning, followed by a period and any other content.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchAnyRecord('80.War and peace. '
        ... 'Ottoman–Polish relations in the 15th-19th centuries. On '
        ... 'the occasion of the exhibition held at the Museum of '
        ... 'Turkish and Islamic Arts in Istanbul, 29.VI.-20.IX.1999. '
        ... 'Selmin Kangal ed. Bartíomiej Õwietlik tr. Istanbul, 1999, '
        ... '462 S.'))
        {'content': 'War and peace. Ottoman–Polish relations in the
             15th-19th centuries. On the occasion of the exhibition held
             at the Museum of Turkish and Islamic Arts in Istanbul,
             29.VI.-20.IX.1999. Selmin Kangal ed. Bartíomiej Õwietlik
             tr. Istanbul, 1999, 462 S.',
         'number': {'number': 80, 'raw': '80'},
         'raw': '80.War and peace. Ottoman–Polish relations in the
             15th-19th centuries. On the occasion of the exhibition held
             at the Museum of Turkish and Islamic Arts in Istanbul,
             29.VI.-20.IX.1999. Selmin Kangal ed. Bartíomiej Õwietlik
             tr. Istanbul, 1999, 462 S.'}
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        content = lepl.Regexp(r'(?u)(.+)') > 'content'
        all = lepl.Empty() / number / '.' / content / lepl.Eos() > \
            lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber)]

    @staticmethod
    @parsemethod
    def matchBullet():
        """
        This function matches and parses line beginning with a bullet
        and including information relevant to the last record or to the
        current category.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchBullet('\\t\\t•\\tDokumente über '
        ... 'Serbien in den Archiven von Kiev, s. 1860.'))
        {'comment': 'Dokumente über Serbien in den Archiven von Kiev',
         'dot': '•',
         'pointers': [{'pointerEnd': 1860, 'pointerStart': 1860},
                      raw='1860'],
         'raw': '\\t\\t•\\tDokumente über Serbien in den Archiven von
             Kiev, s. 1860.'}
        """
        def remove_comma(input):
            input = input.rstrip()
            if input.endswith(',') or input.endswith(':'):
                input = input[:-1].rstrip()
            return input
        dotIndicator = lepl.Regexp(r'(?u)•') > 'dot'
        comment = lepl.Any()[...] >> remove_comma > 'comment'
        comment2 = lepl.Regexp(r'\D+') >> remove_comma > 'comment'
        referrer = lepl.Literal('s.') & (lepl.Empty() / (lepl.Literal('a') > \
            'referrer') & '.')[:1]
        pointers = lepl.Regexp(r'(?u)([\d,\-ab ]+)\.?') > 'pointers'
        textReferrer = lepl.Literal('s.') / (lepl.Literal('u') > 'referrer') \
            & '.'
        textPointer = lepl.Regexp('([^\.]*)\.?') > 'textPointer'
        ref = (referrer / pointers) | (textReferrer / textPointer)
        result1 = comment & (lepl.Empty() / lepl.Or(',', ':'))[:1] / ref
        result2 = comment2 & (lepl.Empty() / lepl.Or(',', ':'))[:1] / pointers
        all = lepl.Empty() / dotIndicator / (result1 | result2) / lepl.Eos() >\
            lepl.make_dict
        return all, [
            ('pointers', specialparser.parsePointers)]

    @staticmethod
    @parsemethod
    def matchRez():
        """
        This function matches and parses line including reference to a
        review of the publication mentioned in last record (beginning
        with 'Rez.')

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParser.matchRez('Lejla Gaziæ, POF '
        ... '49.2000.359-360.'))
        {'authors': [{'firstnames': ['Lejla'], 'lastname': 'Gaziæ'},
                     raw='Lejla Gaziæ'],
         'raw': 'Lejla Gaziæ, POF 49.2000.359-360.',
         'references': [{'raw': 'POF 49.2000.359-360.',
                         'referenceParts':
                             [{'pages': [{'pageEnd': 360,
                                          'pageStart': 359}],
                               'volume': {'volumeEnd': 49,
                                          'volumeStart': 49},
                               'year': {'yearEnd': 2000,
                                        'yearStart': 2000},
                               'yearPos': 1}],
                               'title': 'POF'},
                              raw='POF 49.2000.359-360.']}
        """
        authors = lepl.Regexp(r'(?u).*(?=, )') > 'authors'
        references = lepl.Regexp(r'(?u)(.*$)') > 'references'
        all = lepl.Empty() / authors / ',' / references / lepl.Eos() > \
            lepl.make_dict
        return all, [
            ('authors', specialparser.parsePersonsReview),
            ('references', specialparser.parseReferences)]

    @classmethod
    def handleRezReference(cls, line):
        """
        This function is for handling lines consisting of Rez. at the
        beginning followed by one or more references separated by '—'.

        >>> from pprint import pprint
        >>> pprint(LineParser.handleRezReference('Rez. Jan GOLDBERG, '
        ... 'ILS 7.3.2000.408-411. — Rashid KHALIDI, '
        ... 'IJMES 32.2.2000.307-308.'))
        [{'authors': [{'firstnames': ['Jan'], 'lastname': 'GOLDBERG'},
                      raw='Jan GOLDBERG'],
          'raw': 'Jan GOLDBERG, ILS 7.3.2000.408-411.',
          'references': [{'raw': 'ILS 7.3.2000.408-411.',
                          'referenceParts':
                              [{'issue': {'volumeEnd': 3,
                                          'volumeStart': 3},
                                'pages': [{'pageEnd': 411,
                                           'pageStart': 408}],
                                'volume': {'volumeEnd': 7,
                                           'volumeStart': 7},
                                'year': {'yearEnd': 2000,
                                         'yearStart': 2000},
                                'yearPos': 2}],
                          'title': 'ILS'},
                         raw='ILS 7.3.2000.408-411.']},
         {'authors': [{'firstnames': ['Rashid'], 'lastname': 'KHALIDI'},
                      raw='Rashid KHALIDI'],
          'raw': 'Rashid KHALIDI, IJMES 32.2.2000.307-308.',
          'references': [{'raw': 'IJMES 32.2.2000.307-308.',
                          'referenceParts':
                              [{'issue': {'volumeEnd': 2,
                                          'volumeStart': 2},
                                'pages': [{'pageEnd': 308,
                                           'pageStart': 307}],
                                'volume': {'volumeEnd': 32,
                                           'volumeStart': 32},
                                'year': {'yearEnd': 2000,
                                         'yearStart': 2000},
                                'yearPos': 2}],
                          'title': 'IJMES'},
                         raw='IJMES 32.2.2000.307-308.']}]
        """
        result = rawlist()
        rezReferences = line.replace('Rez. ', '', 1).split('—')
        for i, rezReference in enumerate(rezReferences):
            if ',' not in rezReference:
                if len(rezReferences) > i + 1:
                    rezReferences[i+1] = rezReference + ' — ' + \
                        rezReferences[i+1]
                else:
                    result.append(rezReference)
            else:
                result.append(cls.matchRez(rezReference.strip()))
        return result

    @classmethod
    def handleTextLinesWRez(cls, line, conferenceRange):
        """
        This function is for handling lines including Rez. in the middle
        of the record.

        >>> from pprint import pprint
        >>> pprint(LineParser.handleTextLinesWRez(159. Nash, Rose. Turkish int'
        ... 'onation. An instrumental study. Den Haag, 1973, 190 S. (Janua lin'
        ... 'guarum, series practica 114). Rez. A. Dab, TDAYB 1973-1974.349-35'
        ... '3.', range(345, 456))

        """
        splitted = line.split('Rez.')
        line = splitted[0]
        record = cls.parseRecordLine(line, conferenceRange)
        line = splitted[1]
        if not isinstance(record, str):
            rezReference = cls.handleRezReference(line)
            record['rezReference'] = rezReference
        return record

    @classmethod
    def parseRecordLine(cls, line, conferenceRange):
        """
        This function parses lines with a number at the beginning.
        The right type of matcher/parser will be found unless the line
        has a mistake.

        >>> from pprint import pprint
        >>> pprint(LineParser.parseRecordLine('3291.Croisades et '
        ... 'pélèrinages. Récits, chroniques et voyages en Terre '
        ... 'sainte, XIIe–XVIIe siècle. Danielle Régnier-Bohler ed. '
        ... 'Paris, 1997, LXXI+ 1438 S.', []))
        {'cities': ['Paris', raw='Paris'],
         'comment': '',
         'number': {'number': 3291, 'raw': '3291'},
         'paginations': [[{'pages': 71, 'roman': True},
                          {'pages': 1438}],
                         raw='LXXI+ 1438'],
         'raw': '3291.Croisades et pélèrinages. Récits, chroniques et
             voyages en Terre sainte, XIIe–XVIIe siècle. Danielle
             Régnier-Bohler ed. Paris, 1997, LXXI+ 1438 S.',
         'title': 'Croisades et pélèrinages. Récits, chroniques et
             voyages en Terre sainte, XIIe–XVIIe siècle. Danielle
             Régnier-Bohler ed.',
         'type': 'collection',
         'year': {'raw': '1997', 'yearEnd': 1997, 'yearStart': 1997}}
        """
        numberMatcher = re.match(r'^([\d]{1,5})\.', line)
        if numberMatcher != None:
            isConference = int(numberMatcher.group(1)) in conferenceRange
            for matcher, type, matcherIsConference in [
                (cls.matchConference, 'conference', True),
                (cls.matchMonograph, 'monograph', False),
                (cls.matchArticle, 'article', False),
                (cls.matchCollection, 'collection', False)]:
                if isConference == matcherIsConference:
                    parsed = matcher(line)
                    if not isinstance(parsed, str):
                        parsed['type'] = type
                        return parsed
            if not isinstance(cls.matchAnyRecord(line), str):
                lineParse = LineParserTa(line)
                lineParse.parseRecord()
                return lineParse.parse
        return {'raw': line, 'type': 'unrecognised'}

    @classmethod
    def parseCategoryLine(cls, line):
        """
        This function tries to parse the line as it was a line representing
        category. In case it is not possible a dictionary with the value of key
        'type' set to 'unrecognised' will be returned.
        """
        parsed = cls.matchCategory(line)
        if not isinstance(parsed, str):
            return parsed
        return {'raw': line, 'type': 'unrecognised'}

    @classmethod
    def parseLineCommentLine(cls, line):
        """
        This function tries to parse the line as it was a line representing
        a comment. In case it is not possible a dictionary with the value of key
        'type' set to 'unrecognised' will be returned.
        """
        if line.startswith('Rez. '):
            return cls.handleRezReference(line)
        for matcher, type in [
            (cls.matchReferateWoTitleWEditor, 'referat'),
            (cls.matchReferateWEditor, 'referat'),
            (cls.matchReferate, 'referat'),
            (cls.matchReferateWoTitle, 'referat'),
            (cls.matchReport, 'bericht'),
            (cls.matchReportWoAuthors, 'bericht')]:
            parsed = matcher(line)
            if not isinstance(parsed, str):
                parsed['type'] = type
                return parsed
        return {'raw': line, 'type': 'unrecognised'}

    @classmethod
    def parseBulletLine(cls, line):
        """
        This function tries to parse the line as it was a line with bullet at
        the beginning. In case it is not possible a dictionary with the value
        of key 'type' set to 'unrecognised' will be returned.
        """
        parsed = cls.matchBullet(line)
        if not isinstance(parsed, str):
            parsed['type'] = 'bullet'
            return parsed
        return {'raw': line, 'type': 'unrecognised'}

    def parseRecord(self):
        """
        This function tries to parse the value of attribute line as it was a
        record from Turkology Annual.
        """
        if self.rawStripped == None:
            Logger.log(self.__class__,
                       self.parseRecord,
                       'Please initialize the instance with a line of '
                           'unparsed data.')
        else:
            conferenceRange = RANGE_CONFERENCE
            self.parse = self.parseRecordLine(self.rawStripped,
                conferenceRange)
            self.parse['raw'] = self.raw
        return self.parse

    def parseCategory(self):
        """
        This function tries to parse the value of attribute line as it was a
        category from Turkology Annual.
        """
        self.parse = self.parseCategoryLine(self.rawStripped)
        self.parse['raw'] = self.raw

    def parseLineComment(self):
        """
        This function tries to parse the value of attribute line as it was a
        a comment from Turkology Annual.
        """
        self.parse = self.parseLineCommentLine(self.rawStripped)
        self.parse['raw'] = self.raw

    def parseBullet(self):
        """
        This function tries to parse the value of attribute line as it was a
        a bullet annotation from Turkology Annual.
        """
        self.parse = self.parseBulletLine(self.rawStripped)
        self.parse['raw'] = self.raw

    @classmethod
    def testTheLine(cls, line):
        """
        This function tries to parse the given line as any of the content
        types from Turkology Annual. If a parse is possible the returned
        value is True. Otherwise False.
        """
        line = cls.stripLine(line)
        result = cls.parseBulletLine(line)
        if result.get('type') != 'unrecognised':
            return True
        result = cls.parseLineCommentLine(line)
        if not isinstance(result, rawlist) and result.get('type') != \
            'unrecognised':
            return True
        result = cls.parseRecordLine(line, RANGE_CONFERENCE)
        if result.get('type') != 'unrecognised':
            return True
        result = cls.parseCategoryLine(line)
        if result.get('type') != 'unrecognised':
            return True
        if len(line.split(' Rez.'))>1:
            result = cls.handleTextLinesWRez(line, RANGE_CONFERENCE)
            if result.get('type') != 'unrecognised':
                return True
        return False

    @staticmethod
    def stripLine(line):
        """
        This function preprocesses the line and substitute all multiple
        spaces by one space starting with the second occurence of multiple
        spaces in the line.
        """
        line = line.replace('  ', ' <<tab>> ', 1)
        line = line.replace('  ', ' ')
        line = line.replace('  ', ' ')
        line = line.replace('<<tab>>', '  ')
        return line

    def __init__(self, line=None):
        """
        Constructor of the class LineParser.
        """
        if line != None:
            self.parse = {}
            self.raw = line
            self.rawStripped = self.stripLine(line)

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
