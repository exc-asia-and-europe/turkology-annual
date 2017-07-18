# Django settings for ta_online project.


from ta_online.search import models  # , editorModels
import re
import os
from sqlalchemy.orm import scoped_session, sessionmaker, clear_mappers
from sqlalchemy import create_engine
from socket import gethostname
from ta_online.search import models
import logging
from logging.handlers import RotatingFileHandler

ROOT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ta_db2',  # Or path to database file if using sqlite3.
        'USER': '',  # Not used with sqlite3.
        'PASSWORD': '',  # Not used with sqlite3.
        'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.
    }
}

DAJAXICE_MEDIA_PREFIX = "dajaxice"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

LOCALEURL_USE_ACCEPT_LANGUAGE = True

PREFIX_DEFAULT_LOCALE = True

LOCALE_INDEPENDENT_PATHS = (
    r'/%s/' % DAJAXICE_MEDIA_PREFIX,
    r'/mylist/export_list',
    r'/mylist/export_entry',
)

LANGUAGES = (('de', 'Deutsch'), ('en', 'English'))

LOGIN_URL = "/admin/login/"

ugettext = lambda s: s

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_DIRECTORY, 'media/')
MEDIA_ROOT = '/home/ta/ta_online/ta_online/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    # 'django.template.loaders.filesystem.Loader',
    # 'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.filesystem.load_template_source',
    # 'django.template.loaders.app_directories.load_template_source',
    # 'django.template.loaders.eggs.load_template_source',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.core.context_processors.i18n',
    'django.contrib.messages.context_processors.messages',
    'ta_online.context_processors.seo.otherLanguages',
    'ta_online.context_processors.seo.canonicalUrl',
    # 'django.contrib.messages.context_processors.request',
)

MIDDLEWARE_CLASSES = (
    # 'django.middleware.cache.UpdateCacheMiddleware', #must be first
    'localeurl.middleware.LocaleURLMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'ta_online.middleware.dbSession.SqlaMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware', #must be last

)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

SESSION_COOKIE_AGE = 18000
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# SESSION_ENGINE = "django.contrib.sessions.backends.file"
# SESSION_FILE_PATH=os.path.join(ROOT_DIRECTORY, "sessions")

ROOT_URLCONF = 'ta_online.urls'

CACHE_BACKEND = 'file:///var/tmp/django_cache'

TEMPLATE_DIRS = os.path.join(ROOT_DIRECTORY, 'templates')

INSTALLED_APPS = (
    'localeurl',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'dajaxice',
    'search',
    'mylist',
    'browse',
    # 'bugfixing',
    # 'compressor',
    # 'admin',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
)

LUCENE_INDEX_DIRECTORY = os.path.join(ROOT_DIRECTORY, "index")

Session = scoped_session(sessionmaker(autoflush=False))

engine = create_engine('postgresql://%s:%s@%s/%s' % (
    DATABASES["default"]["USER"], DATABASES["default"]["PASSWORD"], DATABASES["default"]["HOST"],
    DATABASES["default"]["NAME"]))

clear_mappers()
models.init(engine)

Session.configure(bind=engine)

"""session = []
def getSession():
    if len(session) == 0:
        sqlalchemy.orm.clear_mappers()
        #session.append(models.init(connection='postgresql://ta@localhost/ta_db2'))
        session.append(models.init(connection='postgresql://%s:%s@%s/%s'%(DATABASES["default"]["USER"], DATABASES["default"]["PASSWORD"], DATABASES["default"]["HOST"], DATABASES["default"]["NAME"])))
    return session[0]

editorSession = []
def getEditorSession():
    if len(editorSession) == 0:
        editorSession.append(models.init(connection='postgresql://%s:%s@%s/ta_db'%(DATABASES["default"]["USER"], DATABASES["default"]["PASSWORD"], DATABASES["default"]["HOST"])))
    return editorSession[0]"""

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
# STATIC_ROOT = os.path.join(ROOT_DIRECTORY, 'static')
STATIC_ROOT = '/home/ta/ta_online/ta_online/static/'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
# STATICFILES_DIRS = [os.path.join(ROOT_DIRECTORY, 'media')]
STATICFILES_DIRS = ['/home/ta/ta_online/ta_online/media']

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
    # 'compressor.finders.CompressorFinder',
)

"""COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_CSS_FILTERS = [
    #creates absolute urls from relative ones
    'compressor.filters.css_default.CssAbsoluteFilter',
    #css minimizer
    'compressor.filters.cssmin.CSSMinFilter'
]"""

MAX_LOG_FILE_SIZE_IN_MB = 1000


def create_rotating_log(path):
    """
    Creates a rotating log
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # add a rotating handler
    handler = RotatingFileHandler(path, maxBytes=(10 ** 6) * MAX_LOG_FILE_SIZE_IN_MB, backupCount=5)
    logger.addHandler(handler)


create_rotating_log(os.path.join(ROOT_DIRECTORY, '../log/ta_online.log'))
