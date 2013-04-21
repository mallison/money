from datetime import timedelta

from django.contrib import admin

import models


class TransactionInline(admin.StackedInline):
    model = models.Transaction
    extra = 1
    filter_horizontal = ('tags',)

    def queryset(self, request):
        qs = super(TransactionInline, self).queryset(request)
        # hacky limit for now
        latest = qs.order_by('-date')[0].date - timedelta(1)
        return qs.filter(date__gte=latest)


admin.site.register(models.Account, inlines=[TransactionInline])
admin.site.register(models.Transaction,
                    list_display=('date', 'account', 'memo', 'description', 'amount', 'note'),
                    date_hierarchy='date',
                    filter_horizontal = ('tags',),
                    list_filter=('date',))
admin.site.register(models.Tag)
