#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal
import cctaxjp

# Ledgers -> export

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%d-%m-%y %H:%M:%S%z")

class CoinInfo:
    def __init__(self, local_name, general_name, rank):
        self.local_name = local_name
        self.general_name = general_name
        self.rank = rank
COINS = {
    "USD": CoinInfo('USD', cctaxjp.CoinName.USD, 0),
    "BTC": CoinInfo('BTC', cctaxjp.CoinName.BTC, 1),
    "ETH": CoinInfo('ETH', cctaxjp.CoinName.ETH, 2),
    "IOT": CoinInfo('IOTA', cctaxjp.CoinName.IOTA, 100),
}

def normalize(f, opts):
    reader = csv.reader(f)
    pairs = []
    line = 0
    for rows in reader:
        line += 1
        if len(rows) == 0: continue
        if rows[0] == "#": continue

        r = cctaxjp.Record(
            datetime = parse_datetime(rows[5]),
            source = 'Bitfinex',
            rid = rows[0],
            coin = COINS[rows[2]].general_name,
        )
        amount = Decimal(rows[3])
        if re.match('^Trading fees ', rows[1]):
            r.rtype = cctaxjp.RecordType.FEE
            r.fee = amount
        elif re.match('^Exchange ', rows[1]):
            r.rtype = cctaxjp.RecordType.EXCHANGE
            r.amount = amount
        elif re.match('^Deposit ', rows[1]):
            r.rtype = cctaxjp.RecordType.DEPOSIT
            r.amount = amount
        elif re.match('^Withdraw ', rows[1]):
            r.rtype = cctaxjp.RecordType.WITHDRAW
            r.amount = amount
        elif re.match('^Settlement ', rows[1]):
            r.rtype = cctaxjp.RecordType.SETTLEMENT
            r.amount = amount
        else:
            raise RuntimeError("unknown record type at line {}".format(line))
        print(r.format())

#if __name__ == '__main__':
