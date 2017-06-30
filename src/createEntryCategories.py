from ta_online.settings import getSession
from ta_online.search import models

session = getSession()
session.rollback()
entries = session.query(models.Entry).yield_per(1000)
i = 1
for entry in entries:
	if not entry.category:
		continue
	new = models.EntryCategory(entry.category)
	new.entryId = entry.id
	new.position = 1
	session.add(new)
	print i, new
	i+=1
session.commit()
