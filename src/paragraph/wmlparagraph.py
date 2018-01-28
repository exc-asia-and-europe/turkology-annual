"""
This module includes the WMLParagraph class.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""

import re
from utils.formattedstring import FormattedString

class WMLParagraph(object):
    '''
    This class represents a paragraph within a WML-File together with methods for 
    the paragraph.
    '''
    domPTag = None
    domPPrTag = None
    pStyle = ''
    textRaw = ''
    textLang = {}
    textRStyle = {}
    isRecord = False
    recordNumber = None
    recordBullet = None
    isBullet = False
    tblId = None
    parId = None
    parser = None
    
    def extractPPrTag(self):
        '''
        This function extracts information included in the <w:pPr> tags corresponding to the
        general content of the paragraph.
        '''
        return self.domPTag.getElementsByTagName('w:pPr')[0]
    
    def extractPStyle(self):
        '''
        This function extracts information included in the <w:pStyle> tags corresponding to the
        description of the style of the paragraph.
        '''
        result = None
        if len(self.domPPrTag.getElementsByTagName('w:pStyle'))>0:
            result = self.domPPrTag.getElementsByTagName('w:pStyle')[0].getAttribute('w:val')
        return result
    
    def extractText(self):
        '''
        This function extracts text included in the paragraph.
        '''
        result = ''
        idxStart=0
        for tTag in self.domPTag.getElementsByTagName('w:t'):
            for child in tTag.childNodes:
                if child.nodeType==3:
                    idxEnd = idxStart + len(child.data)
                    result = result + child.data
                    self.textLang.setdefault((idxStart, idxEnd), tTag.parentNode.getElementsByTagName('w:lang')[0].getAttribute('w:val'))
                    self.textRStyle.setdefault((idxStart, idxEnd), tTag.parentNode.getElementsByTagName('w:rStyle')[0].getAttribute('w:val'))
                    idxStart = idxEnd
        return result
    
    def getTextWithLangTags(self):
        '''
        This function returns text included in the paragraph and inserts information on language used 
        in particular segments. 
        '''
        result=''
        for segment in sorted(self.textLang.keys()):
            langId = self.textLang.get(segment)
            (idxStart, idxEnd) = segment
            text = self.textRaw[idxStart:idxEnd]
            part="<lang id=\'%s\'>%s</lang>" %(langId, text)
            result = result + part
        return result      
    
    def getTextSmallCaps(self):
        '''
        This function returns text included in the paragraph with small capitalized letters 
        as capitalized. 
        '''
        result=''
        for segment in sorted(self.textRStyle.keys()):
            styleId = self.textRStyle.get(segment)
            if self.parser.styleToSmallCaps.get(styleId)==True:
                (idxStart, idxEnd) = segment
                text = self.textRaw[idxStart:idxEnd]
                part = text
                part = text.upper()     
                result = result + part
            else:
                (idxStart, idxEnd) = segment
                part = self.textRaw[idxStart:idxEnd] 
                result = result + part
        return result

    
    def getText(self):
        '''
        This function returns text included in the paragraph.
        '''
        result=''
        for segment in sorted(self.textRStyle.keys()):
            styleId = self.textRStyle.get(segment)
            if self.parser.styleToSmallCaps.get(styleId)==True:
                (idxStart, idxEnd) = segment
                text = self.textRaw[idxStart:idxEnd]
                part = text
                result = result + part
            else:
                (idxStart, idxEnd) = segment
                part = self.textRaw[idxStart:idxEnd] 
                result = result + part
        return result
    
    def getTextFormattedSmallCapsWithLangTags(self):
        '''
        This function returns text included in the paragraph with small capitalized letters 
        as capitalized, and tagged with the information on the language used in the particular section. 
        The output is given in the formatted string format.
        '''
        result=''
        for segment in sorted(self.textLang.keys()):
            langId = self.textLang.get(segment)
            (idxStart, idxEnd) = segment
            text = self.getTextSmallCaps()[idxStart:idxEnd]
            part="<lang id=\'%s\'>%s</lang>" %(str(langId), text)
            print(part)
            result = result + part
        return result 
    
    def getTextAsFormattedString(self):
        '''
        This function returns text included in the paragraph with small capitalized letters 
        as capitalized. 
        The output is given in the formatted string format.
        '''
        result = FormattedString('')
        for segment in sorted(self.textLang.keys()):
            langId = self.textLang.get(segment)
            (idxStart, idxEnd) = segment
            text = self.getText()[idxStart:idxEnd]
            part = FormattedString(text, langId)
            result = result + part
        return result
    
    def __init__(self, domStructure, paragraphId=None, tblId=None, parser=None):
        '''
        Constructor
        '''
        try:
            self.textLang = {}
            self.textRStyle = {}
            self.tblId=tblId
            self.parser=parser
            self.parId = paragraphId
            self.domPTag = domStructure
            self.domPPrTag = self.extractPPrTag()
            self.pStyle = self.extractPStyle()
            self.textRaw = self.extractText().strip()
#            print(self.textRaw)
#            print(self.getTextWithLangTags())
#            print(self.getTextSmallCaps())
#            print(self.getTextFormattedSmallCapsWithLangTags())
        except Exception:
            print('Exception in the following Paragraph:  \n' + str(self.domPTag.toxml()))
            raise
