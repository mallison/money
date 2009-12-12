# add in a bunch of dummy transacations 

import datetime
import random

# local imports
import personal_finance.money.models as models


if __name__ == '__main__':
    date = datetime.date(2009, 1, 1)
    account = models.Account.objects.get(name="Barclays")
    for days in range(100):
        models.Transaction.objects.create(
            account=account,
            date=date,
            amount=random.randint(-1000, 1000))
        date += datetime.timedelta(1)

            
            
