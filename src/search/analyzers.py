import lucene
from org.apache.lucene.analysis.standard import StandardAnalyzer, StandardTokenizer
from org.apache.lucene.analysis.core import LowerCaseFilter
from org.apache.lucene.analysis.miscellaneous import ASCIIFoldingFilter


class PorterStemmerAnalyzer(StandardAnalyzer):
    def tokenStream(self, fieldName, reader):
        result = Tokenizer(lucene.Version.LUCENE_CURRENT, reader)
        result = LowerCaseFilter(result)
        if fieldName.endswith("-normalized"):
            result = ASCIIFoldingFilter(result)
        return result

    def getPositionIncrementGap(self):
        return 100
