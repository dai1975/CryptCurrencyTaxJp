#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from decimal import Decimal
import decimal
import cctaxjp

class Balance:
    def __init__(self):
        pass
    def delta(self, r):
        b = Decimal('0') if r.coin not in self.balance else self.balance[r.coin]
        if r.amount is not None: b += r.amount
        if r.exfee is not None: b += r.exfee
        if b < 0 and r.coin not in self.warn:
            if r.source == 'Bitfinex' and r.rtype in [ cctaxjp.RecordType.FEE, cctaxjp.RecordType.SETTLEMENT ]:
                pass
            else:
                print('WARN: %s balance is minus line at %d' % (r.coin, self.line))
        self.balance[r.coin] = b
        r.balance = b
        return r

    def parse(self, f):
        reader = csv.reader(f)
        self.balance = {}
        self.warn = {}
        self.line = 0
        for rows in reader:
            self.line += 1
            r = cctaxjp.Record.parse(rows)
            if r is None:
                continue
            if r.coin is not None:
                self.delta(r)
            print(r.format())
        for k,v in self.balance.items():
            if 0 != v: print("{} {}".format(k,v))

def calc_balance(f):
    Balance().parse(f)
