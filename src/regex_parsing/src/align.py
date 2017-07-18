"""This module aligns the pdf input which was converted to special text
and the wordml input."""
import re
from utils.formattedstring import FormattedString

def _getLines(file):
    """Gets the lines of the pdf input files."""
    page = 1
    while True:
        try:
            line = next(file)
            if line.startswith('\x0c'): page += 1
            pos = tuple(map(float, next(file).split()))
            yield line, page, pos
        except StopIteration:
            return

def align(xmlText, pdfFile):
    """Aligns the xml input and the pdf input."""
    feeder = Feeder(xmlText)
    position = None
    for line, page, newPosition in _getLines(pdfFile):
        if position and (line.startswith('Referate:') or
            line.startswith('Bericht:') or line.startswith('•') or
            line.startswith('Rez.')):
            output = feeder.emit()
            yield output, page, position
            position = newPosition
        output = feeder.feed(line)
        position = addPositions(position, newPosition)
        if output:
            yield output, page, position
            position = None
        if feeder.atEnd(): return

def addPositions(position1, position2):
    """Adds to aligning positions to one position."""
    if position1 == None: return position2
    x11, y11, x21, y21 = position1
    x12, y12, x22, y22 = position2
    return min(x11, x12), min(y11, y12), max(x21, x22), max(y21, y22)

class Feeder(object):
    """Feeder class for processing the xml file."""
    def __init__(self, text):
        if isinstance(text, FormattedString):
            newline = FormattedString('\n')
        else:
            newline = '\n'
        self._text = newline.join((line.strip() for line in text.splitlines()
            if line)) + newline
        self._length = len(self._text)
        self._pos = 0
        self._emitPos = 0

    @staticmethod
    def _strip(text):
        """Substitutes all non-letters with nothing and make the text
        lowercase.
        """ 
        return re.sub(r'[\W_]', '', text.lower())

    def feed(self, text):
        """Feeds text to the feeder."""
        while not (self._text[self._pos].isalnum() or
                self._text[self._pos] == '\n'):
            self._pos += 1
        for char in self._strip(text):
            if self._text[self._pos].lower() == char:
                while True:
                    self._pos += 1
                    if self._text[self._pos].isalnum() or \
                            self._text[self._pos] == '\n':
                        break
            else:
                print(self._text[self._pos-100:self._pos+100])
                print('At char:', self._text[self._pos])
                raise Exception("Feeding error at position %d." % self._pos)
        if self._text[self._pos] == '\n':
            self._pos += 1
            return self.emit()

    def emit(self):
        """Emits text from the feeder."""
        result = self._text[self._emitPos:self._pos]
        self._emitPos = self._pos
        return result.strip()
    
    def atEnd(self):
        """Checks whether we are at the end."""
        return self._pos >= self._length
