from django.conf import settings
from django.db import models
from django.db.models import Q

INITIAL_BALANCE = sum(settings.INITIAL_BALANCES.values())


class Account(models.Model):
    sort_code = models.CharField(max_length=6)
    number = models.CharField(max_length=8)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey(
        Account, null=True, related_name="transactions")
    date = models.DateField()
    amount = models.IntegerField()  # in pence
    memo = models.TextField()
    description = models.TextField(blank=True)
    note = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ('-date', '-memo')

    def account_balance(self, max_date=None):
        previous = self.__class__.objects.filter(account=self.account).filter(
            # TODO: this will be incorrect if two transactions have
            # the same date and memo (but I'm kind of assuming that
            # doesn't happen!)
            Q(date__lt=self.date) | Q(date=self.date) & Q(memo__lte=self.memo)
            ).values_list('amount', flat=True)
        if max_date:
            previous = previous.filter(date__lte=max_date)
        # TODO: can do this with aggregations now
        return sum(previous) + settings.INITIAL_BALANCES[self.account.name]

    def total_balance(self):
        previous = self.__class__.objects.filter(
            # TODO: this will be incorrect if two transactions have
            # the same date and memo (but I'm kind of assuming that
            # doesn't happen!)
            Q(date__lt=self.date) | Q(date=self.date) & Q(memo__lte=self.memo)
            ).exclude(tags__name="transfer").values_list('amount', flat=True)
        # TODO: can do this with aggregations now
        return sum(previous) + INITIAL_BALANCE

    def since_pay_day_balance(self):
        last_pay_day = self.__class__.objects.filter(
            tags__name='salary',
            date__lte=self.date
        ).order_by('-date')[0]
        previous = self.__class__.objects.exclude(tags__name__in=["transfer", "interest"]).filter(
            Q(date__lt=self.date) | Q(date=self.date) & Q(memo__lte=self.memo)
        ).filter(date__gte=last_pay_day.date)
        return previous.aggregate(
            sum=models.Sum('amount'))['sum'] - last_pay_day.amount
        
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
