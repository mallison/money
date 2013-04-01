from django.conf import settings
from django.db import models
from django.db.models import Q

INITIAL_BALANCE = settings.INITIAL_BALANCE


class Account(models.Model):
    sort_code = models.CharField(max_length=6)
    number = models.CharField(max_length=8)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey(Account, null=True)
    date = models.DateField()
    amount = models.IntegerField()  # in pence
    memo = models.TextField()
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('-date', '-memo')

    def balance(self):
        previous = self.__class__.objects.filter(
            # TODO: this will be incorrect if two transactions have
            # the same date and memo (but I'm kind of assuming that
            # doesn't happen!)
            Q(date__lt=self.date) | Q(date=self.date) & Q(memo__lte=self.memo)
            ).values_list('amount', flat=True)
        # TODO: can do this with aggregations now
        return sum(previous) + INITIAL_BALANCE

    def _format_amount(self, amount):
        return '%.2f' % (amount / 100.00)

    def display_amount(self):
        return self._format_amount(self.amount)

    def display_balance(self):
        return self._format_amount(self.balance())


class Tag(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __unicode__(self):
        return self.name


class Payment(models.Model):
    """
    Regular payment from an account
    """
    payee = models.CharField(max_length=255)
    # TODO support start, stop, frequency etc.
    day_of_month = models.PositiveIntegerField()
    amount = models.PositiveIntegerField()
