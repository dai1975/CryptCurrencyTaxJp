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
            logger = lambda s: print("{} at line {} in {}: {}".format(s, f.name, self.line, ",".join(rows)))
            try:
                r = cctaxjp.Record.parse(rows)
                if r is None:
                    continue
                if r.coin is None:
                    raise RuntimeError('coin is empty')
                if r.infee is not None and 0 < r.infee:
                    raise RuntimeError('infee must be less than or equal to 0: {}'.format(r.infee))
                if r.exfee is not None and 0 < r.exfee:
                    raise RuntimeError('exfee must be less than or equal to 0: {}'.format(r.exfee))
                if r.rtype is not None:
                    if r.amount < 0 and r.rtype in [ cctaxjp.RecordType.DEPOSIT, cctaxjp.RecordType.MINING, cctaxjp.RecordType.AIRDROP, cctaxjp.RecordType.LENDING ]:
                        raise RuntimeError('{} must be greater than or equal to 0: {}'.format(r.rtype, r.amount))
                    elif 0 < r.amount and r.rtype in [ cctaxjp.RecordType.INFEE, cctaxjp.RecordType.EXFEE, cctaxjp.RecordType.WITHDRAWAL ]:
                        raise RuntimeError('{} must be less than or equal to 0: {}'.format(r.rtype, r.amount))
                self.delta(r)
                print(r.format())
            except Exception as e:
                logger("ERROR: " + str(e))
                raise
        for k,v in self.balance.items():
            if 0 != v: print("{} {}".format(k,v))

def calc_balance(f):
    Balance().parse(f)
