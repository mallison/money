import re

from mechanize import Browser

br = Browser()
br.set_debug_http(True)
br.set_debug_responses(True)
br.set_debug_redirects(True)



I = 0
def save(func, *args, **kwargs):
    global I
    resp = func(*args, **kwargs)
    page = resp.read()
    filename = 'page%s.html' % I
    I += 1
    with open(filename, 'w') as f:
        f.write(page)
    return page

def login():
    save(br.open, 'https://retail.santander.co.uk/LOGSUK_NS_ENS/BtoChannelDriver.ssobto?dse_operationName=LOGON')
    br.select_form('formCustomerID_1')
    br['infoLDAP_E.customerID'] = '7767598534'
    challenge = save(br.submit)
    br.select_form(nr=0)
    if 'Place of Birth' in challenge:
        answer = 'Stranraer'
    else:
        raise NotImplementedError
    br['cbQuestionChallenge.responseUser'] = answer
    save(br.submit)
    br.select_form('formCustomerID_1')
    br['infoLDAP_E.customerID'] = '7767598534'
    challenge = save(br.submit)



if __name__ == '__main__':
    login()


