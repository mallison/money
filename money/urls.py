from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^$', views.home),

    (r'^untagged/$', views.untagged),

    (r'^load/$', views.load),

    (r'^summary/(\d+)/$', views.summary),

    (r'^save/note/$', views.save_note),

    (r'^save/tags/$', views.save_tags),
)
