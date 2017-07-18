from configparser import ConfigParser

_config = ConfigParser()
try:
    _config.readfp(open('config.conf'))
except:
    _config.readfp(open('../config.conf'))

DOT = "•"

OUTPUT_PREFIX = _config.get('output', 'prefix')
INPUT_FILE = _config.get('input', 'file')
INPUT_PDF_FILE = _config.get('input', 'pdftxt')
START_CONFERENCE = _config.getint('conferences', 'start')
END_CONFERENCE = (_config.getint('conferences', 'end'))+1

RANGE_CONFERENCE = range(START_CONFERENCE, END_CONFERENCE)

# Import the right tome parser
taNumber = _config.get('TA', 'TA-Number')
if taNumber == '1':
    from lineparsers.lineparserta1 import LineParserTa
elif taNumber == '2':
    from lineparsers.lineparserta2 import LineParserTa
elif taNumber == '3':
    from lineparsers.lineparserta3 import LineParserTa
elif taNumber == '4':
    from lineparsers.lineparserta4 import LineParserTa
elif taNumber == '5':
    from lineparsers.lineparserta5 import LineParserTa
elif taNumber == '6':
    from lineparsers.lineparserta6 import LineParserTa
elif taNumber == '7':
    from lineparsers.lineparserta7 import LineParserTa
elif taNumber == '8':
    from lineparsers.lineparserta8 import LineParserTa
elif taNumber == '9':
    from lineparsers.lineparserta9 import LineParserTa
elif taNumber == '10':
    from lineparsers.lineparserta10 import LineParserTa
elif taNumber == '11':
    from lineparsers.lineparserta11 import LineParserTa
elif taNumber == '12':
    from lineparsers.lineparserta12 import LineParserTa
elif taNumber == '13':
    from lineparsers.lineparserta13 import LineParserTa
elif taNumber == '14':
    from lineparsers.lineparserta14 import LineParserTa
elif taNumber == '15':
    from lineparsers.lineparserta15 import LineParserTa
elif taNumber == '16':
    from lineparsers.lineparserta16 import LineParserTa
elif taNumber == '17':
    from lineparsers.lineparserta17 import LineParserTa
elif taNumber == '18':
    from lineparsers.lineparserta18 import LineParserTa
elif taNumber == '19':
    from lineparsers.lineparserta19 import LineParserTa
elif taNumber == '20':
    from lineparsers.lineparserta20 import LineParserTa
elif taNumber == '21':
    from lineparsers.lineparserta21 import LineParserTa
elif taNumber == '22':
    from lineparsers.lineparserta22 import LineParserTa
elif taNumber == '23':
    from lineparsers.lineparserta22 import LineParserTa
elif taNumber == '22-23':
    from lineparsers.lineparserta22 import LineParserTa
elif taNumber == '24':
    from lineparsers.lineparserta24 import LineParserTa
elif taNumber == '25':
    from lineparsers.lineparserta25 import LineParserTa
elif taNumber == '26':
    from lineparsers.lineparserta26 import LineParserTa
else:
    print('Please give the right number of TA-Tome in config.conf')
