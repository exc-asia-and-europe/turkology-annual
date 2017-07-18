"""
This module includes the WMLTbl class.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""
from wordmlparser.wmlparagraph import WMLParagraph

class WMLTbl(object):
    '''
    This class corresponds to the content of <w:tbl> tags within the WML-Document. 
    The <w:tbl> tags principally symbolize a table, and there is mostly one table on one page.
    '''
    domTbl = None
    tblId = None
    paragraphs=[]
    parser = None
    
    def extractParagraphs(self):
        '''
        This method extracts particular paragraphs tagged as <w:pPr> from the WML-Document,
        for each found <w:pPr> the corresponding WMLParagraph instance is initialized and
        saven into a list,
        which is then returned.        
        '''
        result = []
        idx = 0
        for tcTag in self.domTbl.getElementsByTagName('w:tc'):
            for pTag in tcTag.getElementsByTagName('w:p'):
                for child in pTag.childNodes:
                    if child.nodeName=='w:pPr':
                        result.append(WMLParagraph(pTag, idx, self.tblId, self.parser))     
                        idx+=1
        return result  

    def __init__(self, domStructure, tblId=None, parser=None):
        '''
        Constructor
        '''
        self.tblId = tblId
        self.parser = parser
        self.domTbl = domStructure
        self.paragraphs = self.extractParagraphs()
        