"""Helper functions for handling sets of transactions"""

from django.db.models import Sum

from money import models


def totals_for_tags(transactions):
    for name, total in (
        models.Tag.objects
        .filter(transaction__in=transactions)
        .distinct()
        .annotate(sum=Sum('transaction__amount'))
        .order_by('sum')
        .values_list('name', 'sum')
    ):
        # TODO can I do the math in the query?
        yield name, total / 100.0
        # TODO untagged transactions


def in_and_out(transactions):
    for selector in ('amount__gte', 'amount__lt'):
        filtered_transactions = transactions.filter(
            **{selector: 0}
              ).exclude(
            # exclude savings as it's not income
            tags__name="savings").values_list('amount', flat=True)
        # TODO: no ORM way to do the summing?
        yield sum(filtered_transactions) / 100.0
    yield -sum(
        transactions.filter(tags__name="savings")
        .values_list('amount', flat=True)) / 100
