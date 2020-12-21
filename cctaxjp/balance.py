#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from decimal import Decimal
import cctaxjp

class Balance:
    def __init__(self):
        pass
    def delta(self, d):
        b = Decimal('0') if d.coin not in self.balance else self.balance[d.coin]
        if d.amount is not None: b += d.amount
        if d.fee is not None: b += d.fee
        if b < 0 and d.coin not in self.warn:
            print('WARN: %s balance is minus line at %d' % (d.coin, self.line))
            self.warn[d.coin] = True
        self.balance[d.coin] = b
        d.balance = b
        #print(d.coin + ': ' + str(self.balance[d.coin]))
        return d

    def parse(self, f):
        reader = csv.reader(f)
        self.balance = {}
        self.warn = {}
        self.line = 0
        for rows in reader:
            self.line += 1
            r = cctaxjp.Record.parse(rows)
            if r is None: continue

            if r.gain.coin is not None:
                self.delta(r.gain)
            if r.lose.coin is not None:
                self.delta(r.lose)
            print(r.format())
        for k,v in self.balance.items():
            if 0 < v: print("{} {}".format(k,v))

def calc_balance(f):
    Balance().parse(f)
