from django.db import models

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
    description = models.TextField()
    note = models.TextField()
    tags = models.ManyToManyField('Tag')

    def balance(self):
        # TODO: can't rely on PKs for this!!!!!!!!!
        previous = self.__class__.objects.filter(pk__gte=self.pk).values_list('amount', flat=True)
        return sum(previous)

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
