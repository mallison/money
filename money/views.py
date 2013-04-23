import datetime

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
# TODO: figure out csrf with ajax, csrf_exempt is a temp hack for now
from django.views.decorators.csrf import csrf_exempt
from dateutils import relativedelta

# TODO: not sure this is a good style of import (but Guido seems to do
# it in appengine examples)
import loading
import models
from money.transaction import totals_for_tags, in_and_out, account_balances


def home(request, template_name="money/home.html"):
    # summarize each month
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
    # average spending across categories
    first = models.Transaction.objects.order_by('date')[0].date
    last = models.Transaction.objects.order_by('-date')[0].date
    last = datetime.date(last.year, last.month, 1)
    tags = totals_for_tags(models.Transaction.objects.filter(date__lt=last))
    days = (last - first).days
    # TODO how to calculate whole number of months (relativedelta?)?
    approx_months = days / 30.0
    for i in range(len(tags)):
        tags[i] = (tags[i][0], tags[i][1] / approx_months)
    # where am I at this month?
    today = datetime.date.today()
    outstanding = -settings.SAVINGS_TARGET
    this_month = models.Transaction.objects.filter(
        date__year=today.year,
        date__month=today.month)
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        if not this_month.filter(
            memo__contains=details['memo']).exists():
            outstanding += details['amount']
    # where am I this year?
    before_this_month = models.Transaction.objects.filter(
        date__lt=datetime.date(today.year, today.month, 1))
    before_this_month_total = before_this_month.aggregate(sum=Sum('amount'))
    before_this_month = before_this_month.all()
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        before_this_month = before_this_month.exclude(
            memo__contains=details['memo'])
    average_daily_non_regular_spending = (
        before_this_month.aggregate(sum=Sum('amount'))['sum'] /
        days)
    # TODO this isn't quite right for the rest of the year
    monthly_approximate = sum(
        r['amount'] for r in settings.REGULAR_TRANSACTIONS.values())
    daily_approximate = monthly_approximate / 30.0
    end_of_year = datetime.date(today.year, 12, 31)
    days = end_of_year - today
    for i in range(len(tags)):
        tags[i] = (tags[i][0], tags[i][1], tags[i][1] * days.days / 30.0)
    after_this_month = days.days * (
        daily_approximate + average_daily_non_regular_spending)
    estimated_remaining_regular_spend_for_year = []
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        estimated_remaining_regular_spend_for_year.append(
            (transaction, details['amount'], details['amount'] / 30.0 * days.days))
    # TODO factor known future exprenditure
    return render(
        request, template_name,
        {
            'latest_transaction': latest_transaction,
            'balances': account_balances(models.Transaction.objects.all()),
            'months': months,
            'this_month': months[-1],
            'overall_total': models.Transaction.objects.aggregate(
                sum=Sum('amount')),
            'tags': tags,
            'outstanding': outstanding,
            'before_this_month': before_this_month_total,
            'after_this_month': after_this_month,
            'regular_monthly_amount': monthly_approximate,
            'non_regular_monthly_amount': average_daily_non_regular_spending * 30,
            'savings_target': settings.SAVINGS_TARGET,
            'estimated_remaining_regular_spend_for_year': estimated_remaining_regular_spend_for_year,
            })


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
        if '1-2-3' in account:
            parser = loading.santander_credit_card
        elif 'santander' in account:
            parser = loading.santander
        elif 'virgin' in account:
            parser = loading.virgin
        elif 'west brom' in account:
            parser = loading.westbrom
        elif 'halifax' in account:
            parser = loading.halifax
        # TODO Barclaycard
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
