# -*- coding: utf-8 -*-

import lepl # Parser Module for Python (2.6+ and 3+) http://www.acooke.org/lepl/index.html - vor allem zu testzwecken, um richtige Regex zu entwickeln
import sys, re
import pickle
from lineparsers.lineparser import LineParser
from utils.constantandconfig import DOT, taNumber
from utils.parsemethod import parsemethod, clearMemoTables
import align

"""
This module takes filename as the argument. The content of the file is parsed into different bibliographic categories.
"""

class RecordParser(object):
    '''
    This class
    '''
    filename = ''
    documentInLines=[]
    documentParsed=None
    outputFile=''
    unrecognizedFile = ''

    @staticmethod
    @parsemethod
    def matchAuthorsNameInIndex():
        """
        """
        familyName = lepl.Regexp(r'(?u).*(?=, )') > 'familyName'
        initials = lepl.Regexp(r'(?u)[^\d^be]*(\.|\))') > 'initials'
        numbers = lepl.Regexp(r'(?u).*') > 'numbers'
        all = lepl.Empty() / familyName / ',' / initials / numbers / lepl.Eos() > lepl.make_dict
        return all

    @staticmethod
    def textDataToLines(filename):
        """
        Reads the content of the given file (file should be encoded as UTF-8) and returns list of lines in the file.
        """
        inputFile = open(filename, 'r', encoding='utf8')
        result = inputFile.read()
        inputFile.close
        result = result.splitlines()
        return result

    @staticmethod
    def pickledDataToLines(filename):
        """
        """
        inputFile = open(filename, 'rb')
        result = pickle.load(inputFile)
        inputFile.close
        result = result.splitlines()
        return result

    @classmethod
    def parseTextLines(cls, lines):
        """
        This function iterate over list of strings and parses using above functions.
        It returns tuple containing a list of identified publications and a list of identified categories.

        Example:

        >>> recordParser=RecordParser(None)
        >>> l=['DIF. Religion, Ordenswesen, Mystik\', '\\t\\t•\\tTagung, s. 300, 302-303.\', '\\t\\t•\\tSufische und religiöse Literatur, s. 979, 1007, 1021.\', '2717.\\tAbu-Manneh, Butrus     The Válî Necip Paóa and the Qádirî order in Iraq. In: JHSu 1-2.2000.115-122.\', "2718.\\tAhmet Súrrú Dedebaba'nún “Bektáóî Tarikatú”. H. Yilmaz tr. In: HBVAD 10.1999.27-49.\", "2719.\\tAkyol, Taha     Osmanlú'da ve Úran'da mezhep ve devlet. Ústanbul, 1999, 261 S.\"]
        >>> recordParser.parseTextLines(l)
        ([{'category': {'categoryRaw': 'DIF. Religion, Ordenswesen, Mystfik\', 'categoryParsed': {'catName': 'Religion, Ordenswesen, Mystik', 'catLabel': 'DIF'}}, 'reference': 'JHSu 1-2.2000.115-122.', 'title': 'The Válî Necip Paóa and the Qádirî order in Iraq.', 'number': '2717', 'authors': 'Abu-Manneh, Butrus  ', 'type': 'article'}, {'content': "Ahmet Súrrú Dedebaba'nún “Bektáóî Tarikatú”. H. Yilmaz tr. In: HBVAD 10.1999.27-49.", 'category': {'categoryRaw': 'DIF. Religion, Ordenswesen, Mystik\', 'categoryParsed': {'catName': 'Religion, Ordenswesen, Mystik', 'catLabel': 'DIF'}}, 'type': 'unknown', 'number': '2718'}, {'comment': '', 'city': 'Ústanbul', 'title': "Osmanlú'da ve Úran'da mezhep ve devlet.", 'authors': 'Akyol, Taha  ', 'number': '2719', 'year': '1999', 'category': {'categoryRaw': 'DIF. Religion, Ordenswesen, Mystik\', 'categoryParsed': {'catName': 'Religion, Ordenswesen, Mystik', 'catLabel': 'DIF'}}, 'type': 'monography', 'pages': '261'}], [{'categoryRaw': 'DIF. Religion, Ordenswesen, Mystik\', 'categoryParsed': {'catName': 'Religion, Ordenswesen, Mystik', 'catLabel': 'DIF'}}])
        """
        authorNamesIndex=[]
        publications = []
        categories = []
        index = 0
        length = len(lines)
        while index < length:
            clearMemoTables()
            current, currentPage, currentPosition = lines[index]
            print(current)
            if (index < len(lines) - 1 and
                currentPage != lines[index+1][1] and
                (current.endswith(']') or
                 current.endswith('.')) and
                (lines[index+1][0].startswith('Referate:') or
                 lines[index+1][0].startswith('Bericht:') or
                 lines[index+1][0].startswith('•') or
                 lines[index+1][0].startswith('Rez.'))):
                index += 1
            elif (index < length - 1 and
                  currentPage != lines[index+1][1]):
                if index < length - 2:
                    handledNewpage = cls.handleNewpage(lines[index][0],
                                                       lines[index+1][0],
                                                       lines[index+2][0])
                else:
                    handledNewpage = cls.handleNewpage(lines[index][0],
                                                       lines[index+1][0], '')
                current = handledNewpage[0]
                index += handledNewpage[1]
            else:
                index += 1
            numberMatcher = re.match(r'^([\d]{1,5})\.', current)
            catLabelMatcher = re.match(r'^([A-Z]{1,5})\.', current)
            if len(publications)>0:
                lastRecord = True
            else:
                lastRecord = False
            if len(categories)>0:
                currentCategory = categories[-1]
            else:
                currentCategory = None
            currentRecord = None
            currentLineComment = None
            currentBullet = None
            if numberMatcher is not None:
                lineParse = LineParser(current)
                lineParse.parseRecord()
                currentRecord = lineParse.parse
                currentRecord['taVolume'] = int(taNumber)
                currentRecord['category'] = currentCategory
                currentRecord['scanPage'] = currentPage
                currentRecord['scanPosition1'] = currentPosition
                publications.append(currentRecord)
            elif catLabelMatcher is not None:
                lineParse = LineParser(current)
                lineParse.parseCategory()
                currentCategory = lineParse.parse
                currentCategory['taVolume'] = int(taNumber)
                currentCategory['scanPage'] = currentPage
                currentCategory['scanPosition1'] = currentPosition
                categories.append(currentCategory)
            elif (current.startswith('Referate:') or
                  current.startswith('Bericht:') or
                  current.startswith('Rez.')):
                lineParse = LineParser(current)
                lineParse.parseLineComment()
                currentLineComment = lineParse.parse
                if lastRecord:
                    if 'lineComments' in publications[-1].keys():
                        publications[-1]['lineComments'].append(currentLineComment)
                    else:
                        publications[-1]['lineComments'] = []
                        publications[-1]['lineComments'].append(currentLineComment)
                    if publications[-1]['scanPage'] == currentPage:
                        publications[-1]['scanPosition1'] = align.addPositions(publications[-1].get('scanPosition1'), currentPosition)
                    else:
                        publications[-1]['scanPosition2'] = align.addPositions(publications[-1].get('scanPosition2'), currentPosition)
            elif current.startswith(DOT):
                lineParse = LineParser(current)
                lineParse.parseBullet()
                currentBullet = lineParse.parse
                currentBullet['taVolume'] = int(taNumber)
                currentBullet['category'] = currentCategory
                currentBullet['scanPage'] = currentPage
                currentBullet['scanPosition1'] = currentPosition
                publications.append(currentBullet)
            elif cls.matchAuthorsNameInIndex(current) is not None:
                authorNameInIndex={}
                #authorNameInIndex['authorsNameParsed'] = cls.matchAuthorsNameInIndex(current[0])
                authorNameInIndex['content'] = current
                authorNamesIndex.append(authorNameInIndex)
        return publications, categories, authorNamesIndex

    @staticmethod
    def handleNewpage(endLastpage, firstNewpage, secondNewpage):
        if LineParser.testTheLine(endLastpage) is True:
            return endLastpage, 1
        if LineParser.testTheLine(endLastpage+' '+firstNewpage) is True:
            return endLastpage+' '+firstNewpage, 2
        if LineParser.testTheLine(endLastpage+' '+secondNewpage) is True:
            return endLastpage+' '+firstNewpage, 2
        return endLastpage, 1

    def getOutputAsString(self, outputFile = None):
        '''
        '''
        result = ''
        if self.documentParsed is None:
            if self.documentInLines is None:
                sys.stderr.write('Please parse a document first by using RecordParser.parseTextData() or RecordParser.parsePickledData()') #@UndefinedVariable
            else:
                self.documentParsed = self.parseTextLines(self.documentInLines)
        for line in self.documentParsed[0]:
            result=result + str(line) +''
        if outputFile is not None:
            self.outputFile=outputFile
            resultFileName =  self.outputFile
            resultFile = open(resultFileName, 'wb')
            pickle.dump(result, resultFile)
            resultFile.close
        return result

    def getOutputAsList(self, outputFile = None):
        '''
        '''
        result = []
        if self.documentParsed is None:
            if self.documentInLines is None:
                sys.stderr.write('Please parse a document first by using RecordParser.parseTextData() or RecordParser.parsePickledData()') #@UndefinedVariable
            else:
                self.documentParsed = self.parseTextLines(self.documentInLines)
        for line in self.documentParsed[0]:
            result.append(line)
        if outputFile is not None:
            self.outputFile=outputFile
            resultFileName =  self.outputFile
            resultFile = open(resultFileName, 'wb')
            pickle.dump(result, resultFile)
            resultFile.close
        return result

    def parseData(self, lines):
        self.documentParsed = self.parseTextLines(lines)

    def __init__(self):
        pass