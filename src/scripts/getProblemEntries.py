import models
from models import Entry
import sys
import time
from datetime import timedelta
import unicodedata

session = models.init(connection='postgresql://@localhost/ta_db2')
entries = session.query(Entry).yield_per(1000)

problems = []
for entry in entries:
    if entry.problem:
        problems.append(entry)

problemFile = open("problemEntries", "w")
for entry in problems:
    # problemFile.write(entry.__unicode__())
    print entry
problemFile.close()
