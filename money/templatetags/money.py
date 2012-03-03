from django import template

register = template.Library()

from ..models import Tag
from ..transaction import totals_for_tags, in_and_out, remaining_outgoings


@register.inclusion_tag("money/transactions_snippet.html")
def transactions(transactions):
    last_transaction = transactions[0]
    current_balance = last_transaction.balance()
    balance_after_remaining_outgoings = (
        current_balance - remaining_outgoings(last_transaction)) / 100.0
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
    return {
        'transactions': grouped,
        'tags': Tag.objects.order_by('name'),
        'balance_after_remaining_outgoings': balance_after_remaining_outgoings,
        'totals_for_tags': totals_for_tags(transactions),
        'in_and_out': in_and_out(transactions)}
