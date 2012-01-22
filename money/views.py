import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
# TODO: figure out csrf with ajax, csrf_exempt is a temp hack for now
from django.views.decorators.csrf import csrf_exempt

# TODO: not sure this is a good style of import (but Guido seems to do it in appengine examples)
import forms
import loading
import models
from money.transaction import totals_for_tags, in_and_out


def home(request):
    transactions = models.Transaction.objects.all()
    try:
        days = int(request.GET.get('days'))
    except (TypeError, ValueError):
        pass
    else:
        if days > 0:
            transactions = transactions.filter(
                date__gt=datetime.date.today() - datetime.timedelta(days))
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
            transactions = loading.parse_pasted_barclays_online_statement(pasted_data)
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
    return render_to_response('money/tags_snippet.html',
                              {'transaction': transaction,
                               'tags': models.Tag.objects.all()})


def summary(request, year):
    transactions = models.Transaction.objects.filter(date__year=year)
    months = []
    for month in xrange(1, 12):
        transactions_for_month = transactions.filter(date__month=month)
        months.append(
            {'name': datetime.date(2012, month, 1).strftime("%B"),
             'summary': in_and_out(transactions_for_month),
             'tags': totals_for_tags(transactions_for_month),
             })
    # TODO: what's the new way to render to a template?
    return render_to_response(
        'money/summary.txt',
        {'year': year,
         'summary': in_and_out(transactions),
         'tags': totals_for_tags(transactions),
         'months': months
         },
        mimetype="text/plain",
        )
