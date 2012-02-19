import datetime

from django.db.models import Min, Max
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
# TODO: figure out csrf with ajax, csrf_exempt is a temp hack for now
from django.views.decorators.csrf import csrf_exempt

# TODO: not sure this is a good style of import (but Guido seems to do
# it in appengine examples)
import loading
import models
from money.transaction import totals_for_tags, in_and_out, remaining_outgoings


# TODO: class based generic view for home and untagged!
def home(request):
    now =  datetime.date.today()
    transactions = models.Transaction.objects.filter(
        date__month=now.month, date__year=now.year)
    last_transaction = transactions[0]
    current_balance = last_transaction.balance()
    balance_after_remaining_outgoings = (
        current_balance - remaining_outgoings(last_transaction)) / 100.0
    try:
        days = int(request.GET.get('days'))
    except (TypeError, ValueError):
        pass
    else:
        if days > 0:
            transactions = transactions.filter(
                date__gt=datetime.date.today() - datetime.timedelta(days))
    transaction_values = transactions.values(
        'pk', 'date', 'memo', 'amount', 'note', 'tags__pk', 'tags__name')
    # .values on a m2m means we get a record *per* m2m value
    # collapse this down (itertools cleverness to do this??)
    grouped = []
    start_balance = last_transaction.balance()
    for i, r in enumerate(transaction_values):
        if grouped and grouped[-1]['pk'] == r['pk']:
            grouped[-1]['tags'].append((r['tags__pk'], r['tags__name']))
        else:
            # new transaction pk
            if i > 0:
                r['balance'] = grouped[-1]['balance'] - grouped[-1]['amount']
            else:
                r['balance'] = start_balance / 100.0
            r['amount'] = r['amount'] / 100.0
            r['tags'] = [(r['tags__pk'], r['tags__name'])]
            grouped.append(r)

    date_range = transactions.aggregate(Min('date'), Max('date'))
    return render_to_response(
        'money/home.html',
        {'transactions': grouped,
         'tags': models.Tag.objects.order_by('name'),
         'date_range': date_range,
         'balance_after_remaining_outgoings': balance_after_remaining_outgoings,
         'totals_for_tags': totals_for_tags(transactions),
         'in_and_out': in_and_out(transactions)})


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
    if request.method == 'POST':
        pasted_data = request.POST.get('pasted_data')
        try:
            transactions = loading.parse_pasted_barclays_online_statement(
                pasted_data)
        except:
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
    transaction = {'pk': transaction.pk,
                   'tags': [(tag.pk, tag.name) for tag in transaction.tags.all()]}
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
