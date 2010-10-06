from django import forms

import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
