#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
from decimal import Decimal
from datetime import datetime
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S%z")

class CoinInfo:
    def __init__(self, local_name, general_name, rank):
        self.local_name = local_name
        self.general_name = general_name
        self.rank = rank
COINS = {
    "BTC": CoinInfo('BTC', cctaxjp.CoinName.BTC, 0),
    "BNB": CoinInfo('BNB', cctaxjp.CoinName.BNB, 1),
    "XRP": CoinInfo('XRP', cctaxjp.CoinName.XRP, 10),
    "DNT": CoinInfo('DNT', cctaxjp.CoinName.DNT, 100),
    "TRIG": CoinInfo('TRIG', cctaxjp.CoinName.TRIG, 100),
    "ELF": CoinInfo('ELF', cctaxjp.CoinName.ELF, 100),
    "CMT": CoinInfo('CMT', cctaxjp.CoinName.CMT, 100),
}

def d(s):
    return None if s == '' else Decimal(s)

def normalize(f, opts):
    reader = csv.reader(f)
    pairs = []
    line = 0
    for rows in reader:
        line += 1
        if len(rows) == 0: continue
        if rows[0] == "UTC_Time": continue

        dt = parse_datetime(rows[0])

        if rows[2] in ['Buy', 'Sell', 'Fee', 'InFee']:
            i = next((i for i,p in enumerate(pairs) if p[rows[2]] is None), None)
            if i is None:
                i = len(pairs)
                pairs.append({ 'datetime': dt, 'Buy': None, 'Sell': None, 'Fee': None, 'InFee': None })
            p = pairs[i]
            p[rows[2]] = (COINS[rows[3]], rows[4]) # (coin, amount(string))
            if (i == 0) and (p['Buy'] is not None) and (p['Sell'] is not None) and (p['Fee'] is not None or p['InFee'] is not None):
                r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.EXCHANGE, p['Buy'][0].general_name, d(p['Buy'][1]))
                if p['Fee'] is not None: r.exfee = d(p['Fee'][1])
                if p['InFee'] is not None: r.infee = d(p['InFee'][1])
                print(r.format())
                r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.EXCHANGE, p['Sell'][0].general_name, d(p['Sell'][1]))
                print(r.format())
                pairs.pop(0)
        elif rows[2] == 'Deposit':
            r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.DEPOSIT, rows[3], d(rows[4]))
            print(r.format())
        elif rows[2] == 'Withdraw':
            r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.WITHDRAWAL, rows[3], d(rows[4]))
            print(r.format())
        elif rows[2] == 'Small assets exchange BNB':
            if opts['debug']: print("Skip BNB exchange because it maybe merged at line %d" % line)
        elif rows[2] == 'Adjust':
            r = cctaxjp.Record(dt, 'Binance', '', cctaxjp.RecordType.ADJUST, rows[3], d(rows[4]))
            print(r.format())
        else:
            raise RuntimeError("unknown record type %s at %d" % (rows[2], line))

#if __name__ == '__main__':
