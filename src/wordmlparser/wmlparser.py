"""
This module includes the WMLParser class.

It was developed as a contribution to the project Turkology Annual Online
at the Cluster of Excellence "Asia and Europe" at the University of Heidelberg. 
"""


from xml.dom.minidom import *
from wordmlparser.wmltable import WMLTbl
from wordmlparser.wmlparagraph import WMLParagraph
from datetime import datetime
import pickle

class WMLParser(object):
    '''
    This class includes methods for extracting information from WML-Files.
    '''
    domWordDocument = None
    domBody = None
    #domLists = None # Not used (DH)
    domStyles = None
    paragraphs = []
    tbls = []
    styleToSmallCaps = {}
    outputFileName = ''
    
    def extractBody(self):
        '''
        This method extracts the <w:body> node from the WML-Document.
        '''
        for child in self.domWordDocument.childNodes:
            if child.nodeName=='w:body':
                return child
        else:
            raise Exception('Body not found')

    def extractLists(self):
        '''
        This method extracts the <w:list> node from the WML-Document
        '''
        result = None
        for child in self.domWordDocument.childNodes:
            if child.nodeName=='w:lists':
                result = child
        return result  
    
    def extractStyles(self):
        '''
        This method extracts the <w:styles> node from the WML-Document
        '''
        result = None
        for child in self.domWordDocument.childNodes:
            if child.nodeName=='w:styles':
                result = child
        return result 

    def extractParagraphs(self):
        '''
        This method extracts particular paragraphs from the elements of 
        self.tbls list. c.f. def extractTbls for reference.
        '''
        result = []
        for child in self.domBody.getElementsByTagName('wx:sect')[0].childNodes:
            if child.nodeName=='w:tbl':
                table = WMLTbl(child, parser=self)
                for paragraph in table.paragraphs:
                    yield paragraph
            elif child.nodeName == 'w:p':
                yield WMLParagraph(child)

        '''for tbl in self.tbls:
            for paragraph in tbl.paragraphs:
                #print(paragraph.domPTag.toxml())
                result.append(paragraph)
            #result.extend(tbl.paragraphs)
        return result'''
    
    def extractTbls(self):
        '''
        This method extracts the <w:tbl> nodes from the WML-Document,
        for each found <w:tbl> it creates the corresponding WMLTbl instance,
        and returns a list containing them.
        '''
        result = []
        idx = 0
        for child in self.domBody.getElementsByTagName('wx:sect')[0].childNodes:
            if child.nodeName=='w:tbl':
                result.append(WMLTbl(child, idx, self))
                idx+=1
        return result
    
    def extractStyleToSmallCaps(self):
        '''
        This method extracts information on small caps from the document and 
        saves the information about indexes where small caps start and end into
        a dictionary. This mapping is then returned.
        '''
        result= {}
#        print(self.domStyles.childNodes)
        for child in self.domStyles.childNodes:
            if child.getAttribute('w:type')=='character':
                styleId = child.getAttribute('w:styleId')
                smallCapsTags = child.getElementsByTagName('w:smallCaps')
                if len(smallCapsTags)>0:
                    if smallCapsTags[0].getAttribute('w:val')=='on':
                        result.setdefault(styleId, True)
                    else:
                        result.setdefault(styleId, False)
                else:
                    result.setdefault(styleId, False)
        return result
               
    
    def getTxtOutput(self, outputFileName=None):
        '''
        This method return the string output of the whole document. The output is 
        formatted as FormattedString, which enables to use specific methods for this type.
        '''
        result= ''
        for par in self.paragraphs:
            result = result + par.getTextAsFormattedString() + '\n'
        if outputFileName is not None:
            self.outputFileName = outputFileName
            resultFileName = self.outputFileName
            resultFile = open(resultFileName, 'wb')
            pickle.dump(result, resultFile)
            resultFile.close
#        else:
#            self.outputFile ='../../output-txt/test-probe-table' + datetime.today().isoformat().replace(':', '-') +'.txt'
        return result
                            

    def __init__(self, xmlFileName):
        '''
        Constructor
        '''
        try:
            self.domWordDocument = parse(xmlFileName).documentElement
            #self.domLists = self.extractLists()  # Not used (DH)
            self.domStyles = self.extractStyles()
            self.styleToSmallCaps = self.extractStyleToSmallCaps()
            self.domBody = self.extractBody()
            self.tbls = self.extractTbls()
            self.paragraphs = self.extractParagraphs()
#            self.getTxtOutput()
#            self.assignRecordToParagraph()
#            self.printParagraphs()
#            print(self.paragraphDict)
        except Exception:
            print ('Details: \n')
            raise
        
if __name__ == '__main__':
    '''
    '''
    wordml = WMLParser('../../input/TA19.xml') 