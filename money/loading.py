import datetime

from .models import Account


class BlankLine(Exception):
    pass


def clean_date(date):
    try:
        return '%s-%s-%s' % tuple(date.split('/')[::-1])
    except:
        return datetime.datetime.strptime(date, '%d %b %y')


def clean_amount(amount):
    amount = amount.strip()
    if amount:
        amount = int(amount.replace(u'\u00a3', '').
                     replace(',', '').
                     replace('.', ''))
    return amount


def add_detail(transactions, lines):
    line = lines.pop(0)
    line = line.strip()
    if not line:
        raise BlankLine
    transactions[-1]['memo'] += '\n' + line


def parse_pasted_barclays_online_statement(data):
    barclays = Account.objects.get(name="Barclays current account")
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        fields = [f.strip() for f in line.split('\t')]
        transactions.append(
            {'date': clean_date(fields[0]),
             'account': barclays,
             'memo': fields[1],
             'amount': clean_amount(fields[2]) or clean_amount(fields[3])})
        try:
            while True:
                add_detail(transactions, lines)
        except (BlankLine, IndexError):
            pass
    return transactions


def parse_pasted_santander_online_statement(data):
    santander = Account.objects.get(name="Santander current account")
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, memo, amount_in, amount_out, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'account': santander,
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions


def parse_pasted_virgin_online_statement(data):
    account = Account.objects.get(name="Virgin savings")
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, effective_date, memo,\
            amount_out, amount_in, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'account': account,
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions


def parse_pasted_westbrom_online_statement(data):
    account = Account.objects.get(name="West Brom savings")
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, status, memo,\
            amount_in, amount_out, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'account': account,
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions
