"""This module contributes factory for writing lepl parsers more easily."""
from functools import wraps
import sys
import os
import itertools
import lepl

memoTables = []

def addToMemoTables(parser):
    """Adds the memo tables of a parser to an internal list for clearing
    the tables for each entry.
    """ 
    memoTables.append(parser.matcher)

def parsemethod(func):
    """Factory function which turn a function returning a parser to a
    method which parses the input.
    """

    parsers = func()
    if type(parsers) != tuple:
        parser = parsers
        #parser = parser.null_parser(lepl.Configuration(rewriters=[]))

        @wraps(func)
        def decorator(input):
            result = parser.parse(input)
            if result:
                result = result[0]
                result['raw'] = input
                return result
            return input
        return decorator

    elif len(parsers) == 2:
        parser, arg2 = parsers
        #parser = parser.null_parser(lepl.Configuration(rewriters=[]))
        if type(arg2) != list:
            fixer = arg2

            @wraps(func)
            def decorator(input):
                result = parser.parse(fixer(input))
                if result:
                    result = result[0]
                    result['raw'] = input
                    return result
                return input
            return decorator

        else:
            specialParsers = arg2

            @wraps(func)
            def decorator(input):
                result = None
                try:
                    result = parser.parse(input)
                except:
                    pass
                if result:
                    result = result[0]
                    result['raw'] = input
                    for name, specialParser in specialParsers:
                        item = result.get(name)
                        if item != None and not isinstance(item, (dict, list,
                            rawlist)):
                            result[name] = specialParser(item)
                    return result
                return input
            return decorator

    else:
        parser, fixer, specialParsers = parsers
        #parser = parser.null_parser(lepl.Configuration(rewriters=[]))
        addToMemoTables(parser)

        @wraps(func)
        def decorator(input):
            if fixer:
                input = fixer(input)
            result = parser.parse(input)
            if result:
                result = result[0]
                result['raw'] = input
                for name, specialParser in specialParsers:
                    item = result.get(name)
                    if item != None and not isinstance(item, (dict, list,
                        rawlist)):
                        result[name] = specialParser(item)
                return result
            return input
        return decorator

def clearMemoTables():
    """Clear all memo tables."""
    for matcher in memoTables:
        matcher._RMemo__table = {}

def _pprint():
    """Tests whether the calling method is called by pprint."""
    return os.path.basename(sys._getframe(2).f_code.co_filename) == 'pprint.py'

class _rawlisttype(type):
    """Metaclass which gives pprint the __repr__ function of list instead
    the classes own __repr__ function so that pprint is working
    """
    def __getattribute__(self, name):
        if name == '__repr__' and _pprint():
            return list.__repr__
        return super().__getattribute__(name)

class _rawelement:
    """A special element for the list which stores the raw input."""
    def __init__(self, item):
        self.item = item

    def __repr__(self):
        return 'raw=%s' % repr(self.item)

class rawlist(list, metaclass=_rawlisttype):
    """A list which stores also the raw input. All functions work the
    same way as the in a normal list."""
    def __setitem__(self, item, value):
        if item == 'raw':
            self.raw = value
        else:
            super().__setitem__(item, value)

    def __getitem__(self, item):
        if item == 'raw' and hasattr(self, 'raw'):
            return self.raw
        elif hasattr(self, 'raw') and _pprint():
            return (self + [_rawelement(self.raw)]).__getitem__(item)
        else:
            return super().__getitem__(item)

    def __delitem__(self, item):
        if item == 'raw' and hasattr(self, 'raw'):
            del self.raw
        else:
            super().__delitem__(item)

    def __len__(self):
        if hasattr(self, 'raw') and _pprint():
            return super().__len__() + 1
        return super().__len__()

    def __iter__(self):
        if hasattr(self, 'raw') and _pprint():
            return itertools.chain(super().__iter__(), [_rawelement(self.raw)])
        return super().__iter__()

    def __repr__(self):
        if hasattr(self, 'raw'):
            if self:
                return super().__repr__()[:-1] + ', raw=%s]' % repr(self.raw)
            else:
                return '[raw=%s]' % repr(self.raw)
        return super().__repr__()
