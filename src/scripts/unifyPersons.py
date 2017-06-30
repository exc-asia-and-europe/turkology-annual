from ta_online.settings import getSession
from ta_online.search.models import Person
import sys
import codecs

stdout_encoding = sys.stdout.encoding

session = getSession()

people = session.query(Person).yield_per(1000)

personDict = {}
for person in people:
	personDict.setdefault((unicode(person.lastname), tuple([unicode(firstname) for firstname in person.firstnames])), []).append(person.id)
total = people.count()
del people

"""outfile = codecs.open("unifiedPeople.txt", "w", encoding="utf-8")
for person, ids in personDict.items():
	outfile.write("%s, %s\t%s\n"%(person[0], " ".join([firstname for firstname in  person[1]]), ",".join([str(id) for id in ids])))


outfile.close()"""
print "%d Autoren, davon %d verschieden."%(total, len(personDict))
