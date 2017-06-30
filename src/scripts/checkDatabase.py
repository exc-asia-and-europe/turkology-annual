import csv
from ta_online.search import models
import sys

session = models.init(connection='postgresql://:@localhost/ta_db2')
entries = session.query(models.Entry).yield_per(5)
total = entries.count()
print
total, "entries"
total = float(total)
loopcount = 0
setToTrue = 0

positiveDict = {}
totalDict = {}

# Test: Negativer Fall -> True

tests = (
    (lambda entry: entry.problem == True, "Problem"),
    (lambda entry: entry.type in ["unknown", "placeholder"] or entry.title == None, "Fehlender Titel"),
    # (lambda entry: entry.type in ["unknown", "collection", "placeholder"] or entry.authors == None or len(entry.authors) == 0, "Fehlender Autor"),
    (lambda entry: entry.type == "unknown", "Unbekannter Typ"),
)

volumes = range(1, 27)
volumes.remove(23)
for vol in volumes:
    totalDict[vol] = 0
    positiveDict[vol] = {}
    for test, _ in tests:
        positiveDict[vol][test] = 0

for entry in entries:
    loopcount += 1

    if loopcount % 1000 == 0:
        print("%d of %d (%f %%)." % (loopcount, total, loopcount / total * 100))

    if entry.type.endswith("Repetition") or entry.type in ["bullet"]:
        continue

    totalDict[entry.volume] += 1
    for test, _ in tests:
        if test(entry):
            positiveDict[entry.volume][test] += 1

outfile = open("db-results.csv", "w")
writer = csv.writer(outfile, delimiter=";")
columns = ["Volume"]
for _, name in tests:
    columns.append("%s (abs.)" % name)
    columns.append("%s (rel.)" % name)
columns.append("Total")

writer.writerow(columns)

for volume in volumes:
    columns = [volume]
    for test, _ in tests:
        columns.append(positiveDict[volume][test])
        columns.append(str(float(positiveDict[volume][test]) / totalDict[volume]).replace(".", ","))
    columns.append(totalDict[volume])

    writer.writerow(columns)
# outfile.write("%s: %d von %d (%f %%)\n"%(str(volume), volumeDict[volume], totalDict[volume],  (float(volumeDict[volume]) / totalDict[volume]) *100 ))

"""problemTotal = sum(volumeDict.values())
total = sum(totalDict.values())
ratio = (float(problemTotal) / total) * 100
outfile.write("\nTotal: %d von %d (%f %%)"%(problemTotal, total, ratio))"""
outfile.close()

# if entry.problem == False and (entry.type.__str__() == "unknown" or entry.title == None):
#    entry.problem = True
#    setToTrue += 1

# session.commit()
# print setToTrue, "entries tagged as wrong"
