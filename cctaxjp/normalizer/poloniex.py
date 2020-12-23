#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S%z")
def coinname(s):
    return cctaxjp.CoinName.check_value(s)

"""
Date,Market,Category,Type,Price,Amount,Total,Fee,Order Number,Base Total Less Fee,Quote Total Less Fee,Fee Currency,Fee Total
2017-01-04 21:56:14,ARDR/BTC,Exchange,Buy,0.00008953,1116.94404110,0.09999999,0.15%,8445168555,-0.09999999,1115.26862503,ARDR,0.00014999
2017-01-05 05:45:34,ARDR/BTC,Exchange,Sell,0.00010500,1115.26862504,0.11710320,0.15%,8477710980,0.11692754,-1115.26862504,BTC,0.00017565

(Base|Quote) Total Less Fee は手数料込みの増減額だと思うが、上の買って全額売った結果を見て分かるように端数に差が出ている。

Sell は quote fee が発生せず、amount と quote total less fee は一致。
手数料で誤差が出ているのだろう。

Buy は、
  amount = 1116.94404110
  fee = 0.15%
  total less fee = 1115.26862503

amount - total less fee = 1.67541607 を fee と考えられそうだが、

Sell の amount と一致させるには、buy.amount - sell.amount = 1.67541606 で、差額が出ている。

地道に fee レートの積算をすると、 buy.amount * fee = 1.675416061650
この積を少数第9位を切り捨てるか、この fee のまま引き算した結果を切り上げればよさそうだ。
"""
def norm_trade(rows, ctx, opts):
    # Date,Market,Category,Type,Price,Amount,Total,Fee,Order Number,Base Total Less Fee,Quote Total Less Fee,Fee Currency,Fee Total
    # 2017-03-09 00:11:22,BTC/USDT,Exchange,Buy,8064.00000000,0.11359561,916.03499904,0.25%,111641538829,-916.03499904,0.11331162,BTC,2.29008749
    dt = parse_datetime(rows[0])
    mo = re.match('^([A-Z]+)\/([A-Z]+)$', rows[1])
    if mo is None:
        raise RuntimeError('unknown currency pair: ' + rows[1])
    quote = coinname(mo.group(1))
    base = coinname(mo.group(2))

    mo = re.match('^([0-9]*(\.[0-9]*)?)\%$', rows[7])
    if mo is None:
        raise RuntimeError('malformed fee value: ' + rows[7])
    fee_rate = Decimal(mo.group(1)) / 100

    r_quote = cctaxjp.Record(dt, 'Poloniex', rows[8], cctaxjp.RecordType.EXCHANGE, quote)
    r_base  = cctaxjp.Record(dt, 'Poloniex', rows[8], cctaxjp.RecordType.EXCHANGE, base)
    if rows[3] == 'Buy':
        r_quote.amount = Decimal(rows[5])
        r_base.amount  = -Decimal(rows[6])
        r_quote.exfee = -(r_quote.amount * fee_rate).quantize(Decimal('1.0E-7'), ROUND_DOWN)
    else:
        r_quote.amount = -Decimal(rows[5])
        r_base.amount  = Decimal(rows[6])
        r_base.exfee   = -(r_base.amount * fee_rate).quantize(Decimal('1.0E-7'), ROUND_DOWN)
    records = [ r_quote, r_base ] if 0 <= r_quote.amount else [ r_base, r_quote ]
    return records, ctx

def norm_distribution(rows, ctx, opts):
    # date,currency,amount,wallet
    # 2020-02-28,BTT,500.00000000,exchange
    dt = parse_datetime(rows[0] + ' 00:00:00')
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.AIRDROP, coinname(rows[1]), rows[2])
    return [r], ctx

def norm_lending(rows, ctx, opts):
    # Currency,Rate,Amount,Duration,Interest,Fee,Earned,Open,Close
    # BTC,0.00008100,0.00131978,2.00032407,0.00000021,-0.00000003,0.00000018,2020-03-09 05:41:17,2020-03-11 05:41:45
    dt = parse_datetime(rows[8])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.LENDING, coinname(rows[0]), rows[4], exfee=rows[5])
    return [r], ctx

def norm_deposit(rows, ctx, opts):
    # Date,Currency,Amount,Address,Status
    # 2017-03-09 11:22:33,ZEC,0.00046672,t1ZYy...,COMPLETE
    dt = parse_datetime(rows[0])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.DEPOSIT, coinname(rows[1]), rows[2])
    return [r], ctx

def norm_withdrawal(rows, ctx, opts):
    # Date,Currency,Amount,Fee Deducted,Amount - Fee,Address,Status
    # 2017-03-09 11:22:33,BTC,0.20000000,0.00050000,0.1995,3FZQ...,COMPLETE: 7092...
    dt = parse_datetime(rows[0])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.WITHDRAWAL, coinname(rows[1]), "-"+rows[2], infee="-"+rows[3])
    return [r], ctx

def norm_margin_borrowing(rows, ctx, opts):
    # Currency,Rate,Amount,Duration,TotalFee,Open,Close
    raise RuntimeError("not implemented yet")

def get_normalizer(header):
    if header == 'Date,Market,Category,Type,Price,Amount,Total,Fee,Order Number,Base Total Less Fee,Quote Total Less Fee,Fee Currency,Fee Total':
        return norm_trade
    elif header == 'date,currency,amount,wallet':
        return norm_distribution
    elif header == 'Currency,Rate,Amount,Duration,Interest,Fee,Earned,Open,Close':
        return norm_lending
    elif header == 'Date,Currency,Amount,Address,Status':
        return norm_deposit
    elif header == 'Date,Currency,Amount,Fee Deducted,Amount - Fee,Address,Status':
        return norm_withdrawal
    elif header == 'Currency,Rate,Amount,Duration,TotalFee,Open,Close':
        return norm_margin_borrowing
    else:
        return None
