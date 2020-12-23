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
def coinname(s):
    if s == 'IOT':
        return cctaxjp.CoinName.IOTA
    else:
        return cctaxjp.CoinName.check_value(s)

def normalize(rows, ctx, opts):
    r = cctaxjp.Record(
        datetime = parse_datetime(rows[5]),
        source = 'Bitfinex',
        rid = rows[0],
        coin = coinname(rows[2])
    )
    amount = Decimal(rows[3])
    if re.match('^Trading fees ', rows[1]):
        r.rtype = cctaxjp.RecordType.EXFEE
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
    return [r], ctx

def get_normalizer(header):
    if header == '#,DESCRIPTION,CURRENCY,AMOUNT,BALANCE,DATE,WALLET':
        return normalize
    else:
        return None
