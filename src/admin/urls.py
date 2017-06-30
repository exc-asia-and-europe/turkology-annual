from django.conf.urls.defaults import *

urlpatterns = patterns('',
                       # (r'check_database/?$', 'ta_online.admin.views.checkDatabase'),
                       # ('test', 'ta_online.admin.views.test'),
                       url(r'edit_entry/(\d+)/$', 'ta_online.admin.views.editEntry'),
                       url(r'login/$', 'django.contrib.auth.views.login', {'template_name': 'admin/login.html'}),
                       url(r'logout/$', 'django.contrib.auth.views.logout'),
                       url('^$', 'ta_online.admin.views.index', name='admin'),
                       # (r'show_categories/$', 'ta_online.admin.views.showCategories'),
                       url(r'query_log/$', 'ta_online.admin.views.showQueryLog'),
                       url(r'show_objects/(\w+)/$', 'ta_online.admin.views.showObjects'),

                       )
