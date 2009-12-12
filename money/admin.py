from django.contrib import admin

import models

admin.site.register(models.Account)
admin.site.register(models.Transaction,
                    list_display=('account', 'date', 'amount'),
                    date_hierarchy='date',
                    list_filter=('date',))
admin.site.register(models.Tag)
