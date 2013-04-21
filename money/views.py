import calendar
import datetime

from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
# TODO: figure out csrf with ajax, csrf_exempt is a temp hack for now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.dates import ArchiveIndexView
from dateutils import relativedelta

# TODO: not sure this is a good style of import (but Guido seems to do
# it in appengine examples)
import loading
import models
from money.transaction import totals_for_tags, in_and_out, account_balances


class Calendar(calendar.HTMLCalendar):
    def __init__(self, transaction_dates, *args, **kwargs):
        self.transaction_dates = transaction_dates
        super(Calendar, self).__init__(*args, **kwargs)

    def formatmonth(self, year, month, **kwargs):
        self.year = year
        self.month = month
        return super(Calendar, self).formatmonth(year, month, **kwargs)

    def formatday(self, day, weekday):
        cell = super(Calendar, self).formatday(day, weekday)
        try:
            day = datetime.datetime(self.year, self.month, day)
        except ValueError:
            pass
        else:
            if day in self.transaction_dates:
                cell = cell.replace('td', 'td style="background-color:blue"')
        return cell


def home(request):
    latest_transaction = models.Transaction.objects.order_by(
        '-date', '-memo')[0]
    date = models.Transaction.objects.order_by('date')[0].date
    months = []
    while True:
        months_transactions = models.Transaction.objects.filter(
            date__month=date.month,
            date__year=date.year)
        if not months_transactions.count():
            break
        months.append(
            (
                datetime.date(date.year, date.month, 1),
                months_transactions
                .exclude(tags__name='transfer').aggregate(sum=Sum('amount'))
                )
            )
        date += relativedelta(months=1)
    tags = totals_for_tags(models.Transaction.objects.all())
    first = models.Transaction.objects.order_by('date')[0].date
    last = models.Transaction.objects.order_by('-date')[0].date
    days = (last - first).days
    approx_months = days / 30.0
    for i in range(len(tags)):
        tags[i] = (tags[i][0], tags[i][1] / approx_months)
    return render(
        request, 'money/home.html',
        {
            'latest_transaction': latest_transaction,
            'balances': account_balances(models.Transaction.objects.all()),
            'months': months,
            'overall_total': models.Transaction.objects.aggregate(
                sum=Sum('amount')),
            'tags': tags,
            })


class SincePayDayArchiveView(ArchiveIndexView):
    def get_queryset(self):
        queryset = super(SincePayDayArchiveView, self).get_queryset()
        self.last_pay_day = queryset.filter(tags__name="salary").order_by('-date')[0]
        return queryset.filter(date__gte=self.last_pay_day.date)

    def get_context_data(self, **kwargs):
        context = super(SincePayDayArchiveView, self).get_context_data(**kwargs)
        context['title'] = 'Since pay-day'
        month = context['up_text'] = self.last_pay_day.date.strftime('%b').lower()
        context['up'] = reverse('money-month-archive',
                                args=(self.last_pay_day.date.year, month))
        return context


def untagged(request):
    transactions = models.Transaction.objects.filter(tags__isnull=True)
    return render_to_response(
        'money/home.html',
        {'transactions': transactions,
         'tags': models.Tag.objects.order_by('name'),
         'totals_for_tags': totals_for_tags(transactions),
         'in_and_out': in_and_out(transactions)})


@csrf_exempt
def load(request):
    account = request.GET['account']
    if request.method == 'POST':
        account = account.lower()
        if 'santander' in account:
            parser = loading.parse_pasted_santander_online_statement
        elif 'virgin' in account:
            parser = loading.parse_pasted_virgin_online_statement
        elif 'west brom' in account:
            parser = loading.parse_pasted_westbrom_online_statement
        # TODO Halifax, Barclaycard
        pasted_data = request.POST.get('pasted_data')
        try:
            transactions = parser(pasted_data)
        except:
            raise
            errors = ['Oops']
        else:
            for transaction in transactions:
                models.Transaction.objects.create(**transaction)
        return HttpResponseRedirect('/')
    else:
        pasted_data = ""
        errors = ""
    return render_to_response('money/load.html',
                              {'data': pasted_data,
                               'account': account,
                               'errors': errors},
                              context_instance=RequestContext(request))


#@request_POST
@csrf_exempt
def save_note(request):
    transaction = models.Transaction.objects.get(
        pk=request.POST.get('transaction'))
    transaction.note = request.POST.get('note')
    transaction.save()
    return render_to_response('money/note_snippet.html',
                              {'transaction': transaction})


#@request_POST
@csrf_exempt
def save_tags(request):
    transaction = models.Transaction.objects.get(
        pk=request.POST.get('transaction'))
    transaction.tags = models.Tag.objects.filter(
        id__in=request.POST.getlist('tags'))
    transaction.save()
    # tags_snippet expects a dict not an instance
    # (this is a consequence of using .values() for performance in the home view)
    # transaction = {'pk': transaction.pk,
    #                'tags': [(tag.pk, tag.name) for tag in transaction.tags.all()]}
    return render_to_response('money/tags_snippet.html',
                              {'transaction': transaction,
                               'tags': models.Tag.objects.all()})


def summary(request, year):
    transactions = models.Transaction.objects.filter(date__year=year)
    months = []
    for month in xrange(1, 13):
        transactions_for_month = transactions.filter(date__month=month)
        months.append(
            {'name': datetime.date(2012, month, 1).strftime("%B"),
             'summary': in_and_out(transactions_for_month),
             'tags': totals_for_tags(transactions_for_month),
             })
    return render(
        request,
        'money/summary.html',
        {'year': year,
         'summary': in_and_out(transactions),
         'tags': totals_for_tags(transactions),
         'months': months
         },
        )


def activity(request):
    dates = models.Transaction.objects.dates('created', 'day')
    return render(
        request,
        'money/activity.html',
        {'calendar': Calendar(dates).formatyear(2013)}
        )


def this_month(request):
    today = datetime.date.today()
    return HttpResponseRedirect(reverse(
            'money-month-archive',
            args=(today.year, today.strftime('%b').lower())))
