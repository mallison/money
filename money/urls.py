from django.conf.urls.defaults import *

import views

urlpatterns = patterns('',

    (r'^$', views.home),

    (r'^load/$', views.load),

    (r'^save/note/$', views.save_note),

    (r'^save/tags/$', views.save_tags),
)
