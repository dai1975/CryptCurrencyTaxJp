#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from decimal import Decimal
from datetime import datetime
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S%z")
def coinname(s):
    return cctaxjp.CoinName.check_value(s)

def d(s):
    return None if s == '' else Decimal(s)

def normalize(rows, ctx, opts):
    dt = parse_datetime(rows[0])

    if rows[2] in ['Buy', 'Sell', 'Fee']:
        pairs = [] if ctx is None else ctx
        i = next((i for i,p in enumerate(pairs) if p[rows[2]] is None), None)
        if i is None:
            i = len(pairs)
            pairs.append({ 'datetime': dt, 'Buy': None, 'Sell': None, 'Fee': None })
        p = pairs[i]
        p[rows[2]] = (coinname(rows[3]), rows[4]) # (coin, amount(string))
        records = []
        if (i == 0) and (p['Buy'] is not None) and (p['Sell'] is not None) and (p['Fee'] is not None):
            pairs.pop(0)
            buy = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.EXCHANGE, p['Buy'][0], d(p['Buy'][1]))
            if p['Fee'] is not None: buy.exfee = d(p['Fee'][1])
            sell = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.EXCHANGE, p['Sell'][0], d(p['Sell'][1]))
            records = [buy, sell]
        return records, pairs

    elif rows[2] == 'Deposit':
        r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.DEPOSIT, rows[3], d(rows[4]))
        return [r], ctx
    elif rows[2] == 'Withdraw':
        r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.WITHDRAWAL, rows[3], d(rows[4]))
        return [r], ctx
    elif rows[2] == 'Small assets exchange BNB':
        if opts['debug']: print("Skip BNB exchange because it maybe merged at line %d" % line)
        return [], ctx
    elif rows[2] == 'Adjust':
        r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.ADJUST, rows[3], d(rows[4]))
        return [r], ctx
    else:
        raise RuntimeError("unknown record type %s at %d" % (rows[2], line))

def get_normalizer(header):
    if header == 'UTC_Time,Account,Operation,Coin,Change,Remark':
        return normalize
    else:
        return None
