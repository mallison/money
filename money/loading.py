class BlankLine(Exception):
    pass


def clean_date(date):
    return '%s-%s-%s' % tuple(date.split('/')[::-1])


def clean_amount(amount):
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
    transactions = []
    lines = data.splitlines()
    while lines:
        line = lines.pop(0)
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
