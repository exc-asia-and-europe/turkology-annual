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
    pass
elif taNumber == '2':
    pass
elif taNumber == '3':
    pass
elif taNumber == '4':
    pass
elif taNumber == '5':
    pass
elif taNumber == '6':
    pass
elif taNumber == '7':
    pass
elif taNumber == '8':
    pass
elif taNumber == '9':
    pass
elif taNumber == '10':
    pass
elif taNumber == '11':
    pass
elif taNumber == '12':
    pass
elif taNumber == '13':
    pass
elif taNumber == '14':
    pass
elif taNumber == '15':
    pass
elif taNumber == '16':
    pass
elif taNumber == '17':
    pass
elif taNumber == '18':
    pass
elif taNumber == '19':
    pass
elif taNumber == '20':
    pass
elif taNumber == '21':
    pass
elif taNumber == '22':
    pass
elif taNumber == '23':
    pass
elif taNumber == '22-23':
    pass
elif taNumber == '24':
    pass
elif taNumber == '25':
    pass
elif taNumber == '26':
    pass
else:
    print('Please give the right number of TA-Tome in config.conf')
