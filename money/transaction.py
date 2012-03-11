"""Helper functions for handling sets of transactions"""

from operator import itemgetter

from django.db.models import Sum

from money.models import Payment, Tag


def totals_for_tags(transactions):
    totals = [(name, total / 100.0) for name, total in (
            Tag.objects
            .filter(transaction__in=transactions)
            .distinct()
            .annotate(sum=Sum('transaction__amount'))
            .order_by('sum')
            .values_list('name', 'sum')
            )
              ]
    totals.append(('misc', sum(
                transactions.filter(
                    tags__isnull=True
                    ).values_list('amount', flat=True)) / 100.0))
    totals.sort(key=itemgetter(1))
    return totals


def in_and_out(transactions):
    for selector in ('amount__gte', 'amount__lt'):
        filtered_transactions = transactions.filter(
            **{selector: 0}
              ).exclude(
            # exclude savings as it's not income
            tags__name="savings"
            ).values_list('amount', flat=True)
        # TODO: no ORM way to do the summing?
        yield sum(filtered_transactions) / 100.0
    yield -sum(
        transactions.filter(tags__name="savings")
        .values_list('amount', flat=True)) / 100.0


def remaining_outgoings(transaction):
    """
    Calculates outgoings remaining after this transaction

    Arguments:
    - `transaction`:
    """
    remaining = Payment.objects.filter(
        day_of_month__gt=transaction.date.day).aggregate(total=Sum('amount'))
    return remaining['total'] or 0
