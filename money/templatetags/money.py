from django.conf import settings
from django import template

register = template.Library()

from ..models import Tag
from ..transaction import totals_for_tags, in_and_out, account_balances


@register.inclusion_tag("money/transactions_snippet.html")
def transactions(transactions):
    transactions = transactions.order_by('-date', '-memo')
    # transaction_values = transactions.values(
    #     'pk', 'date', 'account__name', 'memo', 'amount', 'note', 'tags__pk', 'tags__name')
    # .values on a m2m means we get a record *per* m2m value
    # collapse this down (itertools cleverness to do this??)
    # grouped = []
    # start_total_balance = last_transaction.total_balance()
    # start_balances = {}
    # for account in Account.objects.all():
    #     try:
    #         last_transaction = transactions.filter(account=account).latest()
    #     except Transaction.DoesNotExist:
    #         pass
    #     else:
    #         start_balances[account.name] = last_transaction.account_balance()
    # for i, r in enumerate(transaction_values):
    #     if grouped and grouped[-1]['pk'] == r['pk']:
    #         grouped[-1]['tags'].append((r['tags__pk'], r['tags__name']))
    #     else:
    #         # new transaction pk
    #         if i > 0:
    #             r['total_balance'] = grouped[-1]['total_balance'] - grouped[-1]['amount']
    #         else:
    #             r['total_balance'] = start_total_balance / 100.0
    #         if grouped and 'account_balance' in grouped[-1]:
    #             if r['account__name'] == grouped[-1]['account__name']:
    #                 r['account_balance'] = grouped[-1]['account_balance'] - grouped[-1]['amount']
    #         else:
    #             r['account_balance'] = start_balances[r['account__name']] / 100.0
    #         r['amount'] = r['amount'] / 100.0
    #         r['tags'] = [(r['tags__pk'], r['tags__name'])]
    #         grouped.append(r)
    outstanding = []
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        if not transactions.filter(
            memo__contains=details['memo']).exists():
            outstanding.append((transaction, details['amount']))
    total_outstanding = sum((o[1] for o in outstanding))
    return {
        'transactions': transactions,
        'tags': Tag.objects.order_by('name'),
        'totals_for_tags': totals_for_tags(transactions),
        'balances': account_balances(transactions),
        'in_and_out': in_and_out(transactions),
        'outstanding': outstanding,
        'total_outstanding': total_outstanding,
        'savings_target': -settings.SAVINGS_TARGET,
        }


@register.filter
def pretty_amount(amount):
    return '%0.2f' % (amount / 100.0)
