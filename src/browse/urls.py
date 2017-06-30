from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('ta_online.browse.views',
                       # Example:
                       # (r'^ta/', include('ta.foo.urls')),

                       # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
                       # to INSTALLED_APPS to enable admin documentation:
                       # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       url(r'ta/', 'browseTa', name='browse_ta'),
                       url(r'^categories/$', 'browseCategories', name='category_tree'),
                       url(r'^categories/(\d+)/$', 'browseCategories', name='browse_categories'),
                       (r'journals/', 'browseJournals'),

                       )
