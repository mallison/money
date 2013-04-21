"""Helper functions for handling sets of transactions"""

from operator import itemgetter

from django.db.models import Sum, Max

from money.models import Tag, Account, Transaction


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
    values = []
    for selector in ('amount__gte', 'amount__lt'):
        filtered_transactions = transactions.filter(
            **{selector: 0}
              ).exclude(
            # exclude savings as it's not income
            tags__name="transfer"
            ).values_list('amount', flat=True)
        # TODO: no ORM way to do the summing?
        values.append(sum(filtered_transactions))
        yield values[-1]
    yield sum(values)
    yield -sum(
        transactions.filter(tags__name="transfer")
        .values_list('amount', flat=True))


def account_balances(transactions):
    latest_date = transactions.order_by('-date')[0].date
    balances = []
    accounts = Account.objects.annotate(
        recent=Max('transactions__date')).order_by('-recent')
    for account in accounts.filter(
        transactions__id__gt=0).distinct():
        latest_transaction = account.transactions.order_by('-date', '-memo')[0]
        balances.append(
            (account.name,
             latest_transaction.account_balance(latest_date) / 100.0,
             latest_transaction,
             )
            )
    balances.append(
        ("TOTAL", sum([b[1] for b in balances])))
    loan_payments = Transaction.objects.filter(
        tags__name="mum's loan",
        date__lte=latest_date)
    balances.append(
        ("Mum's loan",
         loan_payments.aggregate(sum=Sum('amount'))['sum'] / 100.0,
         loan_payments[0],
         )
        )
    return balances
