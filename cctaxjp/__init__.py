# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from decimal import Decimal

from .normalizer import NORMALIZERS
from .normalizer import normalize

from .balance import calc_balance

class RecordType:
    BUY = 'BUY'
    SELL = 'SELL'
    WITHDRAWAL = 'WITHDRAWAL'
    DEPOSIT = 'DEPOSIT'
    MINING = 'MINING'
    AIRDROP = 'AIRDROP'
    LENDING = 'LENDING'
    ALL = [ BUY, SELL, WITHDRAWAL, DEPOSIT, MINING, AIRDROP, LENDING ]

class CoinName:
    DNT = 'DNT'
    BTC = 'BTC'
    TRIG = 'TRIG'
    ELF = 'ELF'
    CMT = 'CMT'
    XRP = 'XRP'
    BNB = 'BNB'
    USD = 'USD'
    ETH = 'ETH'
    ALL = [ DNT, BTC, TRIG, ELF, CMT, XRP, BNB, USD ]

def f(f, *args):
    a = [ "" if a is None else a for a in args ]
    return f.format(*a)
def p(f, p, *args):
    a = [ "{}_{}".format(p, a) for a in args ]
    return f.format(*a)

class Value:
    def __init__(self, usd=None, jpy=None):
        self.usd = usd
        self.jpy = jpy
    @classmethod
    def header(cls, prefix):
        return p("{}", prefix, 'jpy')
    def format(self):
        return f("{}", self.jpy)
    @classmethod
    def parse(cls, rows):
        jpy = None if rows[0] == '' else Decimal(rows[0])
        return cls(jpy=jpy)

class Delta:
    def __init__(self, coin=None, amount=None, fee=None, balance=None, price=Value(), cost=Value()):
        if (coin is not None and coin != ''): CoinName.ALL.index(coin) # raise ValueError
        self.coin = coin
        self.amount = amount
        self.fee = fee
        self.balance = balance
        self.price = price
        self.cost = cost
    @classmethod
    def header(cls, prefix):
        return f("{},{},{}", p("{},{},{},{}", prefix, 'coin', 'amount', 'fee', 'balance'), Value.header(prefix+'_price'), Value.header(prefix+'_cost'))
    def format(self):
        return f("{},{},{},{},{},{}", self.coin, self.amount, self.fee, self.price.format(), self.balance, self.cost.format())
    @classmethod
    def parse(cls, rows):
        coin = None if rows[0] == '' else rows[0]
        amount = None if rows[1] == '' else Decimal(rows[1])
        fee = None if rows[2] == '' else Decimal(rows[2])
        balance = None if rows[3] == '' else Decimal(rows[3])
        price = Value.parse(rows[4:5])
        cost = Value.parse(rows[5:6])
        return cls(coin=coin, amount=amount, fee=fee, balance=balance, price=price, cost=cost)

class Record:
    def __init__(self, source, rid=None, rtype=None, datetime=None, gain=Delta(), lose=Delta(), value=Value(), profit=Value(), expense=Value()):
        if (rtype is not None): RecordType.ALL.index(rtype) # raise ValueError
        self.source = source
        self.rid = rid
        self.rtype = rtype
        self.datetime = datetime
        self.gain = gain
        self.lose = lose
        self.value = value
        self.profit = profit
        self.expense = expense

    @classmethod
    def header(cls):
        return f("{},{},{},{},{},{},{},{},{}", 'datetime', 'source', 'id', 'type', Delta.header("gain"), Delta.header("lose"), Value.header("value"), Value.header("profit"), Value.header("expense"))

    def format(self):
        dt = "" if self.datetime is None else self.datetime.isoformat()
        return f("{},{},{},{},{},{},{},{},{}", dt, self.source, self.rid, self.rtype, self.gain.format(), self.lose.format(), self.value.format(), self.profit.format(), self.expense.format())

    @classmethod
    def parse(cls, rows):
        if len(rows) == 0: return None
        if rows[0] == 'datetime': return None
        dt = None if rows[0] == '' else datetime.fromisoformat(rows[0])
        i=4
        gain = Delta.parse(rows[i:i+6]); i += 6
        lose = Delta.parse(rows[i:i+6]); i += 6
        value = Value.parse(rows[i:i+1]); i += 1
        profit = Value.parse(rows[i:i+1]); i += 1
        expense = Value.parse(rows[i:i+1]); i += 1
        return cls(
            rows[1],
            rid = rows[2],
            rtype = rows[3],
            datetime = dt,
            gain = gain,
            lose = lose,
            value = value,
            profit = profit,
            expense = expense,
        )
