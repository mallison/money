from django.conf.urls.defaults import patterns, url
from django.views.generic.dates import (ArchiveIndexView,
                                        YearArchiveView,
                                        MonthArchiveView,
                                        DayArchiveView)
import models
import views

urlpatterns = patterns(
    '',

    (r'^$', views.home),

    (r'^untagged/$', views.untagged),

    url(r'^load/$', views.load,
        name="money-load",
        ),

    (r'^summary/(\d+)/$', views.summary),

    (r'^save/note/$', views.save_note),

    (r'^save/tags/$', views.save_tags),

    url(r'^transactions/$', ArchiveIndexView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            allow_future=True,
            ),
        name="money-all",
     ),

    (r'^transactions/(?P<year>\d{4})/$', YearArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            make_object_list=True,
            template_name="money/transaction_archive.html",
            )
     ),
    url(r'^transactions/(?P<year>\d{4})/(?P<month>\w{3})/$',
        MonthArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            ),
        name="money-month-archive"
     ),
    (r'^transactions/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$',
     DayArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            )
     ),
    url(r'forecast/$',
        views.home,
        {'template_name': 'money/forecast.html'},
        name="money-forecast"),
)
