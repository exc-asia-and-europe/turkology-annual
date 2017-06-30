from ta_online.search import models
import re
from sqlalchemy import and_
import sys

session = models.init(connection='postgresql://:@localhost/ta_db2')
entries = session.query(models.Entry).yield_per(1000)

def getId(refString):
	volume, number = refString.split(".")
	#volume = int(volume)
	#number = int(number)
	try:
		id = entries.filter(and_(models.Entry.volume == int(volume), models.Entry.number == int(number))).first().id
		return id
	except:
		return None


infile = open(sys.argv[1])
lines = infile.readlines()
infile.close()

idDict = {}

for line in lines:
	refs = re.findall(r"\d+\.\d+", line)
	ids = []	
	for ref in refs:
		ids.append(getId(ref))
	idDict[line.split()[0]] = ids

for id, refIds in idDict.items():
	for refId in refIds:
		if refId:
			print "%s\t%d"%(id, refId)
		else:
			print "%s\tNone"%id

