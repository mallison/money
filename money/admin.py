from django.contrib import admin

import models

class TransactionInline(admin.StackedInline):
    model = models.Transaction

admin.site.register(models.Account, inlines=[TransactionInline])
admin.site.register(models.Transaction,
                    list_display=('date', 'memo', 'description', 'amount', 'note'),
                    date_hierarchy='date',
                    list_filter=('date',))
admin.site.register(models.Tag)
