import datetime

from .models import Account


class BlankLine(Exception):
    pass


def barclays(data):
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        fields = [f.strip() for f in line.split('\t')]
        transactions.append(
            {'date': clean_date(fields[0]),
             'memo': fields[1],
             'amount': clean_amount(fields[2]) or clean_amount(fields[3])})
        try:
            while True:
                add_detail(transactions, lines)
        except (BlankLine, IndexError):
            pass
    return transactions


def add_detail(transactions, lines):
    line = lines.pop(0)
    line = line.strip()
    if not line:
        raise BlankLine
    transactions[-1]['memo'] += '\n' + line


def santander(data):
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, memo, amount_in, amount_out, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions


def santander_credit_card(data):
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0)  # .strip()
        date, card_no, memo, amount_in, amount_out = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions


def virgin(data):
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, memo,\
            amount_out, amount_in, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'memo': memo,
             'amount': clean_amount(amount_in) or clean_amount(amount_out)})
    return transactions


def westbrom(data):
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0).strip()
        date, status, memo,\
            amount_in, amount_out, balance = line.split('\t')
        transactions.append(
            {'date': clean_date(date),
             'memo': memo,
             'amount': clean_amount(amount_in) or -clean_amount(amount_out)})
    return transactions


def halifax(data):
    transactions = []
    lines = data.splitlines()
    # 05 Jun 15	Pc Carlos Alberto,12 Porto PRT	90736000010188272	08 Jun 15	36.78
    while lines:
        line = lines.pop(0).strip()
        if not line:
            continue
        date, memo, ref, _, amount = line.split('\t')
        transactions.append(
            {
                'date': clean_date(date),
                'memo': memo,
                'amount': -clean_amount(amount)
            })
    return transactions


def clean_date(date):
    try:
        return '%s-%s-%s' % tuple(date.split('/')[::-1])
    except:
        return datetime.datetime.strptime(date, '%d %b %y')


def clean_amount(amount):
    cleaned = amount.strip()
    if cleaned:
        cleaned = int(cleaned.replace(u'\u00a3', '').
                      replace(',', '').
                      replace('.', '').
                      replace('CR', '')
        )
        if 'CR' in amount:
            cleaned = -cleaned
    return cleaned
