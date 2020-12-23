# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from decimal import Decimal

from .coin import CoinName
from .normalizer import normalize

from .balance import calc_balance

class RecordType:
    ADJUST = 'ADJUST'
    EXCHANGE = 'EXCHANGE'
    INFEE = 'INFEE'
    EXFEE = 'EXFEE'
    WITHDRAWAL = 'WITHDRAWAL'
    DEPOSIT = 'DEPOSIT'
    MINING = 'MINING'
    AIRDROP = 'AIRDROP'
    LENDING = 'LENDING'
    SETTLEMENT = 'SETTLEMENT'

    @classmethod
    def check_value(cls, x):
        x = x.upper()
        if x in vars(cls).values():
            return x
        else:
            raise ValueError("{} is not defined in RecordType".format(x))

def f(f, *args):
    a = [ "" if a is None else a for a in args ]
    return f.format(*a)
def p(f, p, *args):
    a = [ "{}_{}".format(p, a) for a in args ]
    return f.format(*a)

class Record:
    def __init__(self, datetime=None, source=None, rid=None, rtype=None, coin=None, amount=None, infee=None, exfee=None, balance=None, value=None, profit=None, cost=None):
        if (rtype is not None): RecordType.check_value(rtype) # raise ValueError
        if (coin is not None): CoinName.check_value(coin) # raise ValueError
        def as_decimal(x): return x if type(x) in (type(None), Decimal) else Decimal(x)
        self.datetime = datetime
        self.source = source
        self.rid = rid
        self.rtype = rtype
        self.coin = coin
        self.amount = as_decimal(amount)
        self.infee = as_decimal(infee)
        self.exfee = as_decimal(exfee)
        self.balance = as_decimal(balance)
        self.value = as_decimal(value)
        self.profit = as_decimal(value)
        self.cost = as_decimal(cost)

    @classmethod
    def header(cls):
        return f("{},{},{},{},{},{},{},{}",
                 'datetime', 'source', 'id', 'type', 'coin', 'amount', 'infee', 'exfee', 'balance', 'value', 'profit', 'cost')

    def format(self):
        dt = "" if self.datetime is None else self.datetime.isoformat()
        def d(x): return '' if x is None else '{0:f}'.format(x)
        return f("{},{},{},{},{},{},{},{},{},{},{},{}",
                 dt, self.source, self.rid, self.rtype, self.coin, d(self.amount), d(self.infee), d(self.exfee), d(self.balance), d(self.value), d(self.profit), d(self.cost))

    @classmethod
    def parse(cls, rows):
        if len(rows) == 0: return None
        if rows[0] == 'datetime': return None
        return cls(
            datetime = None if rows[0] == '' else datetime.fromisoformat(rows[0]),
            source   = None if rows[1] == '' else rows[1],
            rid      = None if rows[2] == '' else rows[2],
            rtype    = None if rows[3] == '' else rows[3],
            coin     = None if rows[4] == '' else rows[4],
            amount   = None if rows[5] == '' else Decimal(rows[5]),
            infee    = None if rows[6] == '' else Decimal(rows[6]),
            exfee    = None if rows[7] == '' else Decimal(rows[7]),
            balance  = None if rows[8] == '' else Decimal(rows[8]),
            value    = None if rows[9] == '' else Decimal(rows[9]),
            profit   = None if rows[10] == '' else Decimal(rows[10]),
            cost     = None if rows[11] == '' else Decimal(rows[11])
        )
