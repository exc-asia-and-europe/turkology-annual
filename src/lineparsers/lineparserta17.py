"""
This module includes the LineParserTa class for the 17th volume of Turkology Annual.

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
    def matchArticleWParentInReference():
        """

        """
        number = lepl.Regexp(r'(?u)[\d]{1,4}(?=\.)') > 'number'    
        authors = lepl.Regexp(r'(?u)(.+?)(?=   )') > 'authors'    
        title = lepl.Regexp(r'(?u).*?[\.\?\!][\s]*(?= In:)') > 'title'
        references = lepl.Regexp(r'(?u)(([\w]+ [\d\.-]+ \[[\d]{2,4}\][\d\.-]+\.))') > 'references'
        comment = lepl.Regexp(r'(?u)\[.*\]')[0:1] > 'comment'
        all = lepl.Empty() / number / '.' / authors / '  ' / title / 'In:' / references / comment / lepl.Eos() > lepl.make_dict
        return all, [
            ('number', specialparser.parseNumber),
            ('authors', specialparser.parsePersons),
            ('references', specialparser.parseReferences)]

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
            (self.matchArticleWParentInReference, 'article', False),
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
