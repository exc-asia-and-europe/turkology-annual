class Category(object):
    """Klasse zur Handhabung von Kategorien in allgemeinen Artikellisten, Darstellung als Reiter"""

    def __init__(self, name, count=None, repr=None, active=False):
        self.name = name
        self.active = active
        self.count = count
        if repr:
            self.repr = repr
        else:
            self.repr = name
