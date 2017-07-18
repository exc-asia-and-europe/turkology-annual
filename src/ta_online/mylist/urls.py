from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('ta_online.mylist.views',
    # Example:
    # (r'^ta/', include('ta.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

	url(r'add/(?P<entry_id>\d+)', 'addToMyList', name='mylist_add'),
	url(r'toggle/$', 'toggleMyList', name='mylist_toggle'),
	url(r'remove/(?P<entry_id>\d+)', 'removeFromMyList', name='mylist_remove'),
	url(r'clear/?$', 'clearMyList', name='mylist_clear'),
	url(r'export_list/(\w+)', 'export_list', name='mylist_export_list'),
	url(r'export_entry/(\d+)/(\w+)', 'export_entry', name='mylist_export_entry'),
	url(r'^$', 'showMyList', name="mylist_show"),

)
