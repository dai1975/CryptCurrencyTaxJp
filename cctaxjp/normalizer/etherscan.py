#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S%z")

def normalize(rows, ctx, opts):
    # "Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)","CurrentValue @ $592.43/Eth","TxnFee(ETH)","TxnFee(USD)","Historical $Price/Eth","Status","ErrCode"

    dt = parse_datetime(rows[3])

    if rows[13] == '':
        records = []
        r_in = cctaxjp.Record(dt, 'Etherscan', rows[0], cctaxjp.RecordType.DEPOSIT, cctaxjp.CoinName.ETH, rows[7])
        if r_in.amount != 0: records.append(r_in)

        r_ou = cctaxjp.Record(dt, 'Etherscan', rows[0], cctaxjp.RecordType.WITHDRAWAL, cctaxjp.CoinName.ETH, "-"+rows[8], exfee="-"+rows[10])
        if r_ou.amount != 0 or r_ou.exfee != 0: records.append(r_ou)
    else:
        r_err = cctaxjp.Record(dt, 'Etherscan', rows[0], cctaxjp.RecordType.WITHDRAWAL, cctaxjp.CoinName.ETH, exfee="-"+rows[10])
        records = [ r_err ]
    return records, ctx

def get_normalizer(header):
    if re.match(r'^"Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN\(ETH\)","Value_OUT\(ETH\)","CurrentValue @ \$[0-9\.]+/Eth","TxnFee\(ETH\)","TxnFee\(USD\)","Historical \$Price/Eth","Status","ErrCode"$', header):
        return normalize
    else:
        return None
