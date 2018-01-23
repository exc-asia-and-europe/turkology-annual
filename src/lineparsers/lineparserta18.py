"""
This module includes the LineParserTa class for the 18th volume of Turkology Annual.

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
    def matchArticleRepetitionWDotAtTheEnd():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'
        authors = lepl.Regexp(r'(?u)(.+)(?=   )') > 'authors'
        title = lepl.Regexp(r'(?u)(.*?)(?=\[)') > 'title'
        references = lepl.Regexp(r'(?u)(\[s\.[\s]{0,1}TA .*\]|\[S\.[\s]{0,1}TA .*\])(?=\.)') > 'references'
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
        references = lepl.Regexp(r'(?u)(\[s\.[\s]{0,1}TA .*\]|\[S\.[\s]{0,1}TA .*\]|\[cf\.[\s]{0,1}TA .*\])') > 'references'
        period = lepl.Regexp(r'\.')[0:1]
        all = lepl.Empty() / number / '.' / authors / '  ' / title / references / period / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseTAReferences)]

    @staticmethod
    @parsemethod
    def matchRez():
        """
        """
        authors = lepl.Regexp(r'(?u).*(?=, )') > 'authors'
        reference = lepl.Regexp(r'(?u)(.*$)') > 'reference'
        all = lepl.Empty() / authors / ',' / reference / lepl.Eos() > lepl.make_dict
        return all, [
            ('reference', specialparser.parseReferences)]

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

if __name__ == '__main__':
    import doctest
    doctest.testmod()
