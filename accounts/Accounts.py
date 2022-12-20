#Create a new account
#ensure that the account is created with a balance of 0 and date created of today
from datetime import datetime

from sqlalchemy.testing import db


class Account:
    def __init__(self, balance, date_created):
        self.balance = balance
        self.date_created = date_created

#Heroku dev url.https://github.com/MattToegel/IS601/pull/24
def create_account():
    account = Account(balance=0, date_created=datetime.datetime.now())
    db.session.add(account)
    db.session.commit()
    return account

#Validate that the account balance shows the minimum fundings required for the account to be active.
def validate_account_balance(account):
    if account.balance < 100:
        return False
    else:
        return True


#Insert a new account into the database
def insert_account(account):
    db.session.add(account)
    db.session.commit()


