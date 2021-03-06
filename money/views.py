import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
# TODO: figure out csrf with ajax, csrf_exempt is a temp hack for now
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.dates import ArchiveIndexView

from . import loading
from .import models
from money.transaction import totals_for_tags, in_and_out, account_balances
from . import utils


def home(request, template_name="money/home.html"):
    latest_transaction = models.Transaction.objects.order_by(
        '-date', '-memo')[0]
    monthly_totals = utils.get_monthly_totals()
    whole_months, average_for_tags = utils.average_spending_for_each_tag()
    outstanding = utils.get_this_months_outstanding_spending()
    (
        before_this_month,
        after_this_month,
        regular_spending,
        irregular_spending
    ) = utils.estimate_this_years_balance()
    # savings since started paying into pension
    last_pay_day = models.Transaction.objects.filter(
        tags__name="salary").order_by('-date')[0]
    difference = models.Transaction.objects.filter(
        date__gte="2013-12-01",
        date__lt=last_pay_day.date,
    ).exclude(
        tags__name__in=["transfer", "interest"]
    ).aggregate(sum=Sum('amount'))['sum']
    return render(
        request, template_name,
        {
            'latest_transaction': latest_transaction,
            'balances': account_balances(models.Transaction.objects.all()),
            'months': monthly_totals,
            'this_month': monthly_totals[-1],
            'overall_total': models.Transaction.objects.aggregate(
                sum=Sum('amount')),
            'tags': average_for_tags,
            'outstanding': outstanding,
            'before_this_month': before_this_month,
            'after_this_month': after_this_month,
            'regular_spending': regular_spending,
            'irregular_spending': irregular_spending,
            'savings_target': settings.SAVINGS_TARGET,
            'living_balance': difference,
            })


# class SincePayDayArchiveView(ArchiveIndexView):
#     def get_queryset(self):
#         queryset = super(SincePayDayArchiveView, self).get_queryset()
#         self.last_pay_day = queryset.filter(tags__name="salary").order_by('-date')[0]
#         return queryset.filter(date__gte=self.last_pay_day.date)

#     def get_context_data(self, **kwargs):
#         context = super(SincePayDayArchiveView, self).get_context_data(**kwargs)
#         context['title'] = 'Since pay-day'
#         month = context['up_text'] = self.last_pay_day.date.strftime('%b').lower()
#         context['up'] = reverse('money-month-archive',
#                                 args=(self.last_pay_day.date.year, month))
#         return context


class SincePayDayArchiveView(ArchiveIndexView):
    allow_future = True

    def get_queryset(self):
        queryset = super(SincePayDayArchiveView, self).get_queryset()
        month_number = [datetime.date(2013, i, 1).strftime('%b').lower() for i in range(1, 13)].index(self.kwargs['month']) + 1
        self.this_pay_day = queryset.filter(
            tags__name="salary",
            date__year=self.kwargs['year'],
            date__month=month_number,
        ).order_by('-date')[0]
        try:
            self.next_pay_day = queryset.filter(
                tags__name="salary",
                date__gt=self.this_pay_day.date).order_by('date')[0]
        except IndexError:
            self.next_pay_day = None
        queryset = queryset.filter(
            date__gte=self.this_pay_day.date,
        )
        if self.next_pay_day:
            queryset = queryset.filter(date__lt=self.next_pay_day.date)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SincePayDayArchiveView, self).get_context_data(**kwargs)
        context['title'] = 'Since pay-day'
        month = context['up_text'] = self.this_pay_day.date.strftime('%b').lower()
        context['up'] = reverse('money-month-archive',
                                args=(self.this_pay_day.date.year, month))
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
        account_key = account.lower()
        if '1-2-3' in account_key:
            parser = loading.santander_credit_card
        elif 'santander' in account_key:
            parser = loading.santander
        elif 'virgin' in account_key:
            parser = loading.virgin
        elif 'west brom' in account_key:
            parser = loading.westbrom
        elif 'halifax' in account_key:
            parser = loading.halifax
        elif 'barclays' in account_key:
            parser = loading.barclays
        # TODO Barclaycard
        pasted_data = request.POST.get('pasted_data')
        try:
            transactions = parser(pasted_data)
        except:
            raise
            errors = ['Oops']
        else:
            for transaction in transactions:
                transaction['account'] = models.Account.objects.get(name=account)
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


def isas(request):
    ISAS = [
        'Aldermore ISA',
        'Cheshire ISA',
        'Santander ISA 2012-2013',
        # 'Santander ISA 2013-2014', this transferred to the 2yr one below, Santander relabelled the account, so there's no history for this one
        'Santander 2yr fixed ISA 2014',
        'Santander easy access ISA 2014/2015',
    ]
    transactions = models.Transaction.objects.filter(
        account__name__in=ISAS
    ).order_by('date')
    total = sum(v for k, v in settings.INITIAL_BALANCES.items() if k in ISAS)
    summed = []
    for t in transactions:
        total += t.amount
        summed.append((t, total))
    balances = (
        (i, models.Transaction.objects.filter(
            account__name=i).aggregate(sum=Sum('amount'))['sum'] +
         settings.INITIAL_BALANCES.get(i, 0))
        for i in ISAS
    )
    return render(request, 'money/isas.html', {
        'transactions': summed,
        'balances': balances
    })
