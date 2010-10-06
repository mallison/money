from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

import forms
import loading
import models

def home(request):
    transactions = models.Transaction.objects.all()
    return render_to_response(
        'money/home.html',
        {'transactions': transactions,
         'tags': models.Tag.objects.order_by('name'),
         'totals_for_tags': totals_for_tags(transactions),
         'in_and_out': in_and_out(transactions)})

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
def save_note(request):
    transaction = models.Transaction.objects.get(
        pk=request.POST.get('transaction'))
    transaction.note = request.POST.get('note')
    transaction.save()
    return render_to_response('money/note_snippet.html',
                              {'transaction': transaction})

#@request_POST
def save_tags(request):
    transaction = models.Transaction.objects.get(
        pk=request.POST.get('transaction'))
    transaction.tags = models.Tag.objects.filter(
        id__in=request.POST.getlist('tags'))
    transaction.save()
    return render_to_response('money/tags_snippet.html',
                              {'transaction': transaction,
                               'tags': models.Tag.objects.all()})


## Utils
def totals_for_tags(transactions):
    for tag in models.Tag.objects.all():
        tagged_transactions = transactions.filter(tags=tag).values_list('amount', flat=True)
        yield (tag, sum(tagged_transactions) / 100.0 )
    untagged = transactions.filter(tags__isnull=True).values_list(
        'amount', flat=True)
    if untagged.count():
        yield ({'name': 'misc'}, sum(untagged) / 100.0 )

def in_and_out(transactions):
    for selector in ('amount__gte', 'amount__lt'):
        filtered_transactions = transactions.filter(
            **{selector: 0}).values_list('amount', flat=True)
        yield sum(filtered_transactions) / 100.0
