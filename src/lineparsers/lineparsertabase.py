"""
This module includes the LineParser class.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""

import lepl
import re
from utils import specialparser
from utils.parsemethod import parsemethod, rawlist

class LineParserTaBase(object):
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
        >>> pprint(LineParserTaBase.matchCategory('AE. Museen'))
        {'catLabel': 'AE', 'catName': 'Museen', 'raw': 'AE. Museen'}
        """
        catLabel = lepl.Regexp(r'(?u)([A-Z]{1,5})(?=\.)') > 'catLabel'
        catName = lepl.Regexp(r'(?u)(.*)') > 'catName'
        all = lepl.Empty() / catLabel / '.' / catName / lepl.Eos() > lepl.make_dict
        return all

    @staticmethod
    @parsemethod
    def matchMonograph():
        """
        This function matches and parses line including record
        representing a monograph.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParserTaBase.matchMonograph('815.Yelten, '
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
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?, [\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4},)') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchMonographWoYear():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?,)') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [^\s]+? S.)') > 'cities'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchMonographWoPages():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?, [\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=\.)') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / year / '.'  / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchMonographWDotInCity():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\,]+?, [\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^,]+?)(?=, [\d]{2,4},)') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchMonographWCountry():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?,)') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=,)') > 'cities'
        country = lepl.Regexp(r'(?u)([^\d^,]+?)(?=, [\d]{2,4},)') > 'country'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / cities / ',' / country / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchMasterThesisWoCity():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.*?)(?=  )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=Magisterarbeit,)') > 'title'
        university = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'university'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=. )') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'Magisterarbeit,'/ university / ',' / year / '.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchMasterThesisWCity():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=Magisterarbeit,)') > 'title'
        university = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, )') > 'university'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=. )') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'Magisterarbeit,'/ university / ',' / cities / ',' / year / '.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchDissertationWoCity():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=Diss.,)') > 'title'
        university = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'university'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=. )') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'Diss.,'/ university / ',' / year / '.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchDissertationWCity():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=Diss.,)') > 'title'
        university = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, )') > 'university'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4})(?=. )') > 'year'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'Diss.,'/ university / ',' / cities / ',' / year / '.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear)]

    @staticmethod
    @parsemethod
    def matchArticle():
        """
        This function matches and parses line including record
        representing an article.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParserTaBase.matchArticle('923.Altun, Kudret    '
        ... ' XX. yüzyúlda divan óiiri geleneõini sürdüren Kayserili '
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
        >>> pprint(LineParserTaBase.matchArticle("2711.Yedúyildiz, "
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
    def matchArticleSmallIn():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= in:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'in:' / references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWTaf():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)(([^\[]*\.)|([^\[]*,))(?= Taf.)') > 'references'
        table = lepl.Regexp(r'(?u)(Taf\. [^\[]*)') > 'table'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / table / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWTafSmallIn():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= in:)') > 'title'
        references = lepl.Regexp(r'(?u)(([^\[]*\.)|([^\[]*,))(?= Taf.)') > 'references'
        table = lepl.Regexp(r'(?u)(Taf\. [^\[]*)') > 'table'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'in:' / references / table / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWCommentWDotAtTheEnd():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        comment = lepl.Regexp(r'(?u)(\[.*\])\.') > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWCommentWDotAtTheEndWTaf():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        table = lepl.Regexp(r'(?u)(Taf\. [^\[]*)') > 'table'
        comment = lepl.Regexp(r'(?u)(\[.*\])\.') > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / table / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWComment():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        comment = lepl.Regexp(r'(?u)(\[.*\])') > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchArticleWCommentWComplexTitle():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u).*?[\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)([^\[]*\.)') > 'references'
        comment = lepl.Regexp(r'(?u)(\[.*\])') > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / comment / lepl.Eos() > lepl.make_dict
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
        >>> pprint(LineParserTaBase.matchCollection('3291.Croisades et '
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
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])(?= [^\d^\.^\,]+?, [\d]{2,4})') > 'title'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4}[\-\d]{0,10})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchCollectionWEditor():
        """
        This function matches and parses line including record representing collection.
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])') > 'title'
        editors = lepl.Regexp(r'(?u)(.*)(?=ed.)') > 'editors'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4}[\-\d]{0,10})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / editors / 'ed.' / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('editors', specialparser.parsePersonsReview),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchCollectionWVolume():
        """
        This function matches and parses line including record representing collection.
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])') > 'title'
        volumes = lepl.Regexp(r'(?u)(.*?)(?=, )') > 'volumes'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4}[\-\d]{0,10})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / 'Bd.' / volumes / ',' / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('volumes', specialparser.parseVolumes),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchCollectionWEditorWVolume():
        """
        This function matches and parses line including record representing collection.
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])') > 'title'
        editors = lepl.Regexp(r'(?u)(.*)(?= ed.)') > 'editors'
        volumes = lepl.Regexp(r'(?u)(.*?)(?=, )') > 'volumes'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, [\d]{2,4})') > 'cities'
        year = lepl.Regexp(r'(?u)([\d]{2,4}[\-\d]{0,10})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / editors / 'ed.' / 'Bd.' / volumes / ',' / cities / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('editors', specialparser.parsePersonsReview),
            ('volumes', specialparser.parseVolumes),
            ('cities', specialparser.parseCities),
            ('year', specialparser.parseYear),
            ('paginations', specialparser.parsePaginations)]

    @staticmethod
    @parsemethod
    def matchCollectionWCountryWEditor():
        """
        This function matches and parses line including record representing collection.
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.+?[\.\!\?])') > 'title'
        editors = lepl.Regexp(r'(?u)(.*)(?= ed.)') > 'editors'
        cities = lepl.Regexp(r'(?u)([^\d^\.^,]+?)(?=, )') > 'cities'
        country = lepl.Regexp(r'(?u)(.+?)(?=, [\d]{2,4})') > 'country'
        year = lepl.Regexp(r'(?u)([\d]{2,4}[\-\d]{0,10})(?=, )') > 'year'
        paginations = lepl.Regexp(r'(?u)(.+?)(?= S.)') > 'paginations'
        comment = lepl.Regexp(r'(?u)(.*)')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / title / editors / 'ed.' / cities / ',' / country / ',' / year / ',' / paginations / 'S.' / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('editors', specialparser.parsePersonsReview),
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
        >>> pprint(LineParserTaBase.matchConference("284.    Ankara, "
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
        title = lepl.Regexp(r'(?u)([^\[]*)') > 'title'
        all = lepl.Empty() / number / '.' / cities / ',' / date / ':' / title / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchConferenceWComment():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        date = lepl.Regexp(r'(?u)(.*?)(?=: )') > 'date'
        title = lepl.Regexp(r'(?u)(.*)(?=\[)') > 'title'
        comment = lepl.Regexp(r'(?u)(\[.*\][\.]{0,1})')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / cities / ',' / date / ':' / title / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchConferenceWCountry():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        country = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'country'
        date = lepl.Regexp(r'(?u)(.*?)(?=: )') > 'date'
        title = lepl.Regexp(r'(?u)([^\[]*)') > 'title'
        all = lepl.Empty() / number / '.' / cities / ',' / country / ',' / date / ':' / title / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchConferenceWCountryWComment():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        cities = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'cities'
        country = lepl.Regexp(r'(?u)([^,]+?)(?=, )') > 'country'
        date = lepl.Regexp(r'(?u)(.*?)(?=: )') > 'date'
        title = lepl.Regexp(r'(?u)(.*)(?=\[)') > 'title'
        comment = lepl.Regexp(r'(?u)(\[.*\][\.]{0,1})')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / cities / ',' / country / ',' / date / ':' / title / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('cities', specialparser.parseCities),
            ('date', specialparser.parseDate)]

    @staticmethod
    @parsemethod
    def matchArticleRepetitionWDotAtTheEnd():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=\[)') > 'title'
        references = lepl.Regexp(r'''(?u)((\[s\.[\s]{0,1}TA .*\])|(\[S\.[\s]{0,1}TA .*\])|(\[cf\.[\s]{0,1}TA .*\])|(\[s\.[\s]{0,1}ΤΑ .*\])|(\[S\.[\s]{0,1}ΤΑ .*\])|(\[cf\.[\s]{0,1}ΤΑ .*\]))''') > 'references'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / references / '.' / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseTAReferences)]

    @staticmethod
    @parsemethod
    def matchArticleRepetition():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=\[)') > 'title'
        references = lepl.Regexp(r'''(?u)((\[s\.[\s]{0,1}TA .*\])|(\[S\.[\s]{0,1}TA .*\])|(\[cf\.[\s]{0,1}TA .*\])|(\[s\.[\s]{0,1}ΤΑ .*\])|(\[S\.[\s]{0,1}ΤΑ .*\])|(\[cf\.[\s]{0,1}ΤΑ .*\]))''') > 'references'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / references / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseTAReferences)]

    @staticmethod
    @parsemethod
    def matchCollectionRepetition():
        """
        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        title = lepl.Regexp(r'(?u)(.*?)(?=\[)') > 'title'
        references = lepl.Regexp(r'(?u)(\[s\.[\s]{0,1}TA .*\]|\[S\.[\s]{0,1}TA .*\])(?=\.)') > 'references'
        all = lepl.Empty() / number / '.' / title / references / '.' / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('references', specialparser.parseTAReferences)]

    @staticmethod
    @parsemethod
    def matchRez():
        """
        """
        report = lepl.Regexp(r'(?u)(Bericht)(?=: )') > 'report'
        references = lepl.Regexp(r'(?u)[\s]*([^\d]*)[\s]*([\d].+)') > 'references'
        all = lepl.Empty() / report / ':' / references / lepl.Eos() > lepl.make_dict
        return all, [
            ('references', specialparser.parseReferences)]

    @staticmethod
    @parsemethod
    def matchAnyRecord():
        """
        This function matches and parses line including record including
        record number at the beginning and following content. More
        general than matchCollection / matchArticle / matchMonograph.
        This function helps to find not matched records and will be used
        to develop new funtions or improve existing ones.

        Example:

        >>> from pprint import pprint
        >>> pprint(LineParserTaBase.matchAnyRecord('80.War and peace. '
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
        all = lepl.Empty() / number / '.' / content / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber)]

    @staticmethod
    @parsemethod
    def matchAuthorsNameInIndex():
        """
        """
        familyName = lepl.Regexp(r'(?u).*(?=, )') > 'familyName'
        initials = lepl.Regexp(r'(?u)[^\d^be]*(\.|\))') > 'initials'
        numbers = lepl.Regexp(r'(?u).*') > 'numbers'
        all = lepl.Empty() / familyName / ',' / initials / numbers > lepl.make_dict
        return all

    @classmethod
    def handleRezReference(cls, line):
        """
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
    def getRepetitionMatchers(cls):
        return [
            (cls.matchArticleRepetition, 'articleRepetiton'),
            (cls.matchCollection, 'collectionRepetition')]

    @classmethod
    def handleTextLinesWRez(cls, line):
        """
        """
        splitted = line.split('Rez.')
        line = splitted[0]
        for matcher, type in cls.getRepetitionMatchers():
            try:#XXX try-Block
                parsed = matcher(line)
            except:
                continue
            if not isinstance(parsed, str):
                parsed['type'] = type
                break
        else:
            if cls.matchAnyRecord(line) != None:
                parsed = cls.matchAnyRecord(line)
                parsed['type'] = 'unknown'
            else:
                parsed['type'] = 'unrecognised'
        line = splitted[1]
        if not isinstance(parsed, str):
            rezReference=cls.handleRezReference(line)
            parsed.setdefault('rezReference', rezReference)
        return parsed

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
            (self.matchMonographWDotInCity, 'monograph', False),
            (self.matchMonographWoPages, 'monograph', False),
            (self.matchMonographWoYear, 'monograph', False),
            (self.matchArticleWCommentWDotAtTheEndWTaf, 'article', False),
            (self.matchArticleWTaf, 'article', False),
            (self.matchArticleWTafSmallIn, 'article', False),
            (self.matchArticleWCommentWDotAtTheEnd, 'article', False),
            (self.matchArticleWComment, 'article', False),
            (self.matchArticle, 'article', False),
            (self.matchArticleSmallIn, 'article', False),
            (self.matchArticleWCommentWComplexTitle, 'article', False),
            (self.matchCollectionWEditorWVolume, 'collection', False),
            (self.matchCollectionWCountryWEditor, 'collection', False),
            (self.matchCollectionWEditor, 'collection', False),
            (self.matchCollectionWVolume, 'collection', False),
            (self.matchCollection, 'collection', False),
            (self.matchArticleRepetition, 'articleRepetition', False),
            (self.matchArticleRepetitionWDotAtTheEnd, 'articleRepetition', False),
            (self.matchCollectionRepetition, 'collectionRepetition', False)]

    def parseRecord(self):
        '''
        '''
        line = self.rawStripped
        numberMatcher = re.match(r'^([\d]{1,5})\.', line)
        if numberMatcher != None:
            from utils.constantandconfig import RANGE_CONFERENCE
            isConference = int(numberMatcher.group(1)) in RANGE_CONFERENCE
            if len(line.split('Rez.'))==2:
                self.parse = self.handleTextLinesWRez(line)
                self.parse['raw'] = line
                return
            for matcher, type, matcherIsConference in self.getMatchers():
                if isConference == matcherIsConference:
                    parsed = matcher(line)
                    if not isinstance(parsed, str):
                        self.parse = parsed
                        self.parse['type'] = type
                        self.parse['raw'] = line
                        return
            if self.matchAnyRecord(line) != None:
                self.parse = self.matchAnyRecord(line)
                self.parse['type'] = 'unknown'
                self.parse['raw'] = line
                return
            else:
                self.parse = {'type': 'unrecognised', 'raw': line}
                return
        print(line)

    def __init__(self, line):
        '''
        Constructor
        '''
        line = line.replace('  ', ' <<tab>> ', 1)
        line = line.replace('  ', ' ')
        line = line.replace('  ', ' ')
        line = line.replace('<<tab>>', '  ')
        self.rawStripped = line
        self.parse = {}

if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
