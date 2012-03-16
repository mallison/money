from django.conf.urls.defaults import patterns
from django.views.generic import RedirectView
from django.views.generic.dates import (ArchiveIndexView,
                                        YearArchiveView,
                                        MonthArchiveView,
                                        DayArchiveView)

import models
import views

urlpatterns = patterns(
    '',

    (r'^untagged/$', views.untagged),

    (r'^load/$', views.load),

    (r'^summary/(\d+)/$', views.summary),

    (r'^save/note/$', views.save_note),

    (r'^save/tags/$', views.save_tags),

    (r'^$', RedirectView.as_view(url="transactions/since_pay_day/")),

    (r'^transactions/since_pay_day/$', views.SincePayDayArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            allow_future=True,
            )
     ),

    (r'^transactions/$', ArchiveIndexView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            allow_future=True,
            )
     ),

    (r'^transactions/(?P<year>\d{4})/$', YearArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            make_object_list=True,
            template_name="money/transaction_archive.html",
            )
     ),
    (r'^transactions/(?P<year>\d{4})/(?P<month>\w{3})/$', MonthArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            )
     ),
    (r'^transactions/(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{2})/$',
     DayArchiveView.as_view(
            model=models.Transaction,
            date_field='date',
            template_name="money/transaction_archive.html",
            )
     ),
)
