"""Helper functions for handling sets of transactions"""

from money import models


def totals_for_tags(transactions):
    for tag in models.Tag.objects.all():
        tagged_transactions = transactions.filter(
            tags=tag).values_list('amount', flat=True)
        yield (tag, sum(tagged_transactions) / 100.0)
    untagged = transactions.filter(tags__isnull=True).values_list(
        'amount', flat=True)
    if untagged.count():
        yield ({'name': 'misc'}, sum(untagged) / 100.0)


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
