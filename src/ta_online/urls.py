from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.conf import settings
import os

from dajaxice.core import dajaxice_autodiscover

dajaxice_autodiscover()

urlpatterns = patterns('',
                       # Example:
                       # (r'^ta/', include('ta_online.foo.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
                       # to INSTALLED_APPS to enable admin documentation:
                       # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # (r'^admin/', include('ta_online.admin.site.urls')),
                       (r'^robots\.txt', 'ta_online.search.views.robotsTxt'),
                       (r'^localeurl/', include('localeurl.urls')),
                       (r'^problems/', 'ta_online.search.views.showProblemEntries'),
                       (r'^mylist/', include('ta_online.mylist.urls')),
                       (r'^report_error/', include('ta_online.bugfixing.urls')),
                       # (r'^edit/', include('ta_online.editing.urls')),
                       (r'^i18n/', include('django.conf.urls.i18n')),
                       (r'^admin/', include('ta_online.admin.urls')),
                       url(r'^show_entry/(\d+)/(\d+)', 'ta_online.search.views.showEntry', name='show_entry'),
                       url(r'^show_entry/(\d+)$', 'ta_online.search.views.showEntry', name='show_entry'),
                       url(r'^show_plaintext_entry/(\d+)$', 'ta_online.search.views.showPlainTextEntry'),
                       url(r'^browse/', include('ta_online.browse.urls')),
                       url(r'^prefaces/$', 'ta_online.search.views.prefaces', name='prefaces'),
                       url(r'^prefaces/([\w-]+)', 'ta_online.search.views.showPreface', name='prefaces'),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',
                        {'document_root': os.path.join(settings.ROOT_DIRECTORY, 'media')}),
                       (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
                       url(r'^/?$', 'ta_online.search.views.search', name='home'),
                       url(r'^advanced/?$', 'ta_online.search.views.advancedSearch', name='advanced_search'),
                       )
