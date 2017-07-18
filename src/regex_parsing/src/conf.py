"""This module print the conference data for a specific volume."""
import sys

d = {number: (start, end) for number, start, end in (line.split('\t') for line in open('/Users/nicolas/Desktop/ta_conferences.txt').read().splitlines())}

number = sys.argv[1]
start, end = d[number]
znumber = number.zfill(2)

print('[input]\nfile = ../input/TA%s.xml\npdftxt = ../input/TA%s.txt\n\n[output]\nprefix = ta%s\n\n[conferences]\nstart = %s\nend = %s\n\n[TA]\nTA-Number = %s' % (znumber, znumber, znumber, start, end, number))
