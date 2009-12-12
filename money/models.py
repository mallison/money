from django.db import models


class Account(models.Model):
    sort_code = models.CharField(max_length=6)
    number = models.CharField(max_length=8)
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Transaction(models.Model):
    account = models.ForeignKey(Account)
    date = models.DateField()
    amount = models.IntegerField()  # in pence
    memo = models.TextField()
    description = models.TextField()
    tags = models.ManyToManyField('Tag')


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name
