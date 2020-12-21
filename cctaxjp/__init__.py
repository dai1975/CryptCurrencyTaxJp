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

class Record:
    def __init__(self, datetime=None, source=None, rid=None, rtype=None, coin=None, amount=None, fee=None, balance=None, value=None, profit=None, cost=None):
        if (rtype is not None): RecordType.ALL.index(rtype) # raise ValueError
        if (coin is not None and coin != ''): CoinName.ALL.index(coin) # raise ValueError
        self.datetime = datetime
        self.source = source
        self.rid = rid
        self.rtype = rtype
        self.coin = coin
        self.amount = amount
        self.fee = fee
        self.balance = balance
        self.value = value
        self.profit = value
        self.cost = cost

    @classmethod
    def header(cls):
        return f("{},{},{},{},{},{},{},{}",
                 'datetime', 'source', 'id', 'type', 'coin', 'amount', 'fee', 'balance', 'value', 'profit', 'cost')

    def format(self):
        dt = "" if self.datetime is None else self.datetime.isoformat()
        return f("{},{},{},{},{},{},{},{},{},{},{}",
                 dt, self.source, self.rid, self.rtype, self.coin, self.amount, self.fee, self.balance, self.value, self.profit, self.cost)

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
            fee      = None if rows[6] == '' else Decimal(rows[6]),
            balance  = None if rows[7] == '' else Decimal(rows[7]),
            value    = None if rows[8] == '' else Decimal(rows[8]),
            profit   = None if rows[9] == '' else Decimal(rows[9]),
            cost     = None if rows[10] == '' else Decimal(rows[10])
        )
