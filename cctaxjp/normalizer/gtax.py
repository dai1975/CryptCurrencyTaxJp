#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, timezone
import cctaxjp

JST = timezone(timedelta(hours=+9), 'JST')

def header():
    return '取引所名,日時（JST）,取引種別,取引通貨名(+),取引量(+),取引通貨名(-),取引量(-),取引額時価,手数料通貨名,手数料数量'

TYPE_FORMAT = {
    cctaxjp.RecordType.ADJUST: 'ボーナス',
    cctaxjp.RecordType.EXCHANGE: '売買',
    cctaxjp.RecordType.INFEE: '手数料',
    cctaxjp.RecordType.EXFEE: '手数料',
    cctaxjp.RecordType.WITHDRAWAL: '送付',
    cctaxjp.RecordType.DEPOSIT: '預入',
    cctaxjp.RecordType.MINING: 'マイニング',
    cctaxjp.RecordType.AIRDROP: 'ボーナス',
    cctaxjp.RecordType.LENDING: '売上',
    cctaxjp.RecordType.SETTLEMENT: '送付',
}

def format(r):
    dt = r.datetime.astimezone(JST).strftime("%Y/%m/%d %H:%M:%S")
    typ = TYPE_FORMAT[r.rtype]

    gain = ('', '')
    lose = ('', '')
    fee  = ('', '')
    if r.amount is not None and r.amount != 0:
        if 0 < r.amount:
            gain = (r.coin, str(r.amount))
        else:
            lose = (r.coin, str(-r.amount))
    if r.exfee is not None and r.exfee != 0:
        fee = (r.coin, str(-r.exfee))
    if gain[0] == '' and lose[0] == '' and fee[0] == '':
        return None

    if gain[0] == '' and lose[0] == '':
        typ = '手数料'

    return '{},{},{},{},{},{},{},{},{},{}'.format(r.source, dt, typ, gain[0], gain[1], lose[0], lose[1], "", fee[0], fee[1])

import re
import csv
from datetime import datetime
from decimal import Decimal
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S")

def normalize(rows, ctx, opts):
    # "Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)","CurrentValue @ $592.43/Eth","TxnFee(ETH)","TxnFee(USD)","Historical $Price/Eth","Status","ErrCode"

    dt = parse_datetime(rows[3])

    r_in = cctaxjp.Record(dt, 'Etherscan', rows[0], cctaxjp.RecordType.TRANSFER, cctaxjp.RecordType.ETH, exfee=rows[10])
    r_ou = cctaxjp.Record(dt, 'Etherscan', rows[0], cctaxjp.RecordType.TRANSFER, cctaxjp.RecordType.ETH)
    if rows[13] == '':
        if rows[7] != '': r_in.amount = Decimal(rows[7])
        if rows[8] != '': r_ou.amount = -Decimal(rows[8])
        records = [ r_in, r_ou ]
    else:
        records = [ r_in ]
    return records, ctx

def get_normalizer(header):
    if header == '"Txhash","Blockno","UnixTimestamp","DateTime","From","To","ContractAddress","Value_IN(ETH)","Value_OUT(ETH)","CurrentValue @ $592.43/Eth","TxnFee(ETH)","TxnFee(USD)","Historical $Price/Eth","Status","ErrCode"':
        return normalize
    else:
        return None
