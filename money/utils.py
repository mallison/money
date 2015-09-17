import datetime

from dateutils import relativedelta
from django.conf import settings
from django.db.models import Sum

from . import models
from . import transaction


def get_monthly_totals():
    earliest_transaction_date = \
        models.Transaction.objects.order_by('date')[0].date
    months = []
    date = earliest_transaction_date
    while True:
        months_transactions = models.Transaction.objects.filter(
            date__month=date.month,
            date__year=date.year)
        if not months_transactions.count():
            break
        months.append(
            (
                datetime.date(date.year, date.month, 1),
                months_transactions.exclude(
                    tags__name__in=['transfer', 'interest', "mums's loan"]
                ).aggregate(sum=Sum('amount'))
                )
            )
        date += relativedelta(months=1)
    months.reverse()
    return months


def average_spending_for_each_tag():
    first = models.Transaction.objects.order_by('date')[0].date
    last = models.Transaction.objects.order_by('-date')[0].date
    # Only consider whole months
    last = datetime.date(last.year, last.month, 1)
    tags = transaction.totals_for_tags(
        models.Transaction.objects.filter(date__lt=last))
    months = whole_months_between(first, last)
    for i in range(len(tags)):
        tags[i] = (tags[i][0], tags[i][1] / months)
    return months, tags


def get_this_months_outstanding_spending():
    today = datetime.date.today()
    outstanding = -settings.SAVINGS_TARGET
    this_month = models.Transaction.objects.filter(
        date__year=today.year,
        date__month=today.month)
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        if not this_month.filter(
                memo__contains=details['memo']).exists():
            outstanding += details['amount']
    return outstanding


def estimate_this_years_balance():
    total_to_end_of_last_month = get_total_to_end_of_last_month()
    rest_of_year, regular_spending, irregular_spending = \
        get_estimate_to_end_of_year()
    return (total_to_end_of_last_month, rest_of_year,
            regular_spending, irregular_spending)


def get_total_to_end_of_last_month():
    today = datetime.date.today()
    start_of_year = datetime.date(today.year, 1, 1)
    start_of_month = datetime.date(today.year, today.month, 1)
    total = models.Transaction.objects.filter(
        date__gte=start_of_year,
        date__lt=start_of_month).aggregate(total=Sum('amount'))
    return total['total']


def get_estimate_to_end_of_year():
    # TODO factor in known future exprenditure (holidays, car, ...)
    today = datetime.date.today()
    start_of_month = datetime.date(today.year, today.month, 1)
    end_of_year = datetime.date(today.year + 1, 1, 1)
    average_monthly_non_regular_spend = get_average_monthly_non_regular_spend()
    monthly_regular_spend = get_monthly_regular_spend()
    months = whole_months_between(start_of_month, end_of_year)
    estimate = months * (average_monthly_non_regular_spend +
                         monthly_regular_spend)
    regular_spending = (
        (t, d['amount'], d['amount'] * months)
        for t, d
        in settings.REGULAR_TRANSACTIONS.items())

    __, average_for_tags = average_spending_for_each_tag()
    for i in range(len(average_for_tags)):
        average_for_tags[i] = (average_for_tags[i][0],
                               average_for_tags[i][1],
                               average_for_tags[i][1] * months)

    return estimate, regular_spending, average_for_tags


def get_average_monthly_non_regular_spend():
    today = datetime.date.today()
    start_of_year = datetime.date(today.year, 1, 1)
    start_of_month = datetime.date(today.year, today.month, 1)
    before_this_month = models.Transaction.objects.filter(
        date__gte=start_of_year,
        date__lt=start_of_month).exclude(tags__name="transfer")
    for transaction, details in settings.REGULAR_TRANSACTIONS.items():
        before_this_month = before_this_month.exclude(
            memo__contains=details['memo'])
    months = whole_months_between(start_of_year, start_of_month)
    return 0
    return (
        before_this_month.aggregate(sum=Sum('amount'))['sum'] /
        months * 1.0
    )


def get_monthly_regular_spend():
    return sum((t['amount'] for t in settings.REGULAR_TRANSACTIONS.values()))


def whole_months_between(date1, date2):
    """Calculate the whole number of months between two dates.

    Both dates must be the first of the month.

    >>> import datetime
    >>> whole_months_between(datetime.date(2013, 1, 1),
    ...     datetime.date(2013, 5, 1))
    4

    """
    if date1.day != 1 or date2.day != 1:
        raise ValueError("Dates must be the first of the month")
    months1 = date1.year * 12 + date1.month - 1
    months2 = date2.year * 12 + date2.month - 1
    return months2 - months1
