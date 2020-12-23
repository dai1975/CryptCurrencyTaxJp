#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+" +0000", "%m/%d/%Y %I:%M:%S %p %z")

COINNAME_MAP = {
    'STRAT': 'STRAX',
    'BCC': 'BCH',
}
def coinname(s):
    if s in COINNAME_MAP:
        s = COINNAME_MAP[s]
    return cctaxjp.CoinName.check_value(s)

"""
Web UI:
 - Price: 0.00015680 [btc]
 - Quantity Filled: 1532.14038860 [OK]
 - Actual Rate: 0.00015679 [BTC]
 - Commission: 0.00060059 [BTC]
 - Total: 0.23963902 [BTC]

history:
 - Quantity: 1532.14038860 // quote 単位
 - Limit: 0.00015680
 - CommisionPaid: 0.00060059 // base 単位
 - Price: 0.24023961 // (- 0.24023961 0.00060059)->0.23963902 なので、手数料引く前の base 枚数のようだ
"""
def norm_old_order(rows, ctx, opts):
    # OrderUuid,Exchange,Type,Quantity,Limit,CommissionPaid,Price,Opened,Closed
    rid = rows[0]
    dt = parse_datetime(rows[8])

    mo = re.match('^([A-Z]+)-([A-Z]+)$', rows[1])
    if mo is None:
        raise RuntimeError('malformed currency pair: ' + rows[1])
    quote = coinname(mo.group(2))
    base  = coinname(mo.group(1))

    r_quote = cctaxjp.Record(dt, 'Bittrex', rid, cctaxjp.RecordType.EXCHANGE, quote, rows[3])
    r_base  = cctaxjp.Record(dt, 'Bittrex', rid, cctaxjp.RecordType.EXCHANGE, base, rows[6], exfee="-"+rows[5])
    if rows[2] == 'LIMIT_BUY':
        r_base.amount = -r_base.amount
    elif rows[2] == 'LIMIT_SELL':
        r_quote.amount = -r_quote.amount
    else:
        raise RuntimeError('unknown OrderType: ' + rows[2])
    records = [ r_quote, r_base ] if 0 <= r_quote.amount else [ r_base, r_quote ]
    return records, ctx

"""
00 Uuid xxxxxxx
01 Exchange BTC-ETH // base-quote 表記
02 TimeStamp 9/3/2017 1:32:23 PM
03 OrderType LIMIT_BUY
04 Limit 0.08160003 //差値
05 Quantity 11.55944700 // quote 注文枚数
06 QuantityRemaining 0.00000000 //注文残数
07 Commission 0.00235806 //手数料。commision / price ~= 0.0025 = 0.25% なので、price と同じ単位だろう。
08 Price 0.94325109 //トータル価格 = base通貨枚数。注文残数引いた実売買での枚数
09 PricePerUnit 0.08160002 //単位価格
10 IsConditional False //空文字もある。false と同じかな?
11 Condition
12 ConditionTarget 0.00000000
13 ImmediateOrCancel False
14 Closed 9/3/2017 1:33:51 PM //時刻。未決の注文は載ってなさげ。
15 TimeInForceTypeId 0
16 TimeInForce
(/ 0.00235806 0.94325109)
"""
def norm_order(rows, ctx, opts):
    # Uuid,Exchange,TimeStamp,OrderType,Limit,Quantity,QuantityRemaining,Commission,Price,PricePerUnit,IsConditional,Condition,ConditionTarget,ImmediateOrCancel,Closed,TimeInForceTypeId,TimeInForce
    # xxxxxxx,BTC-ETH,9/3/2017 1:32:23 PM,LIMIT_BUY,0.08160003,11.55944700,0.00000000,0.00235806,0.94325109,0.08160002,False,,0.00000000,False,8/1/2017 1:33:51 PM,0,

    rid = rows[0]
    dt = parse_datetime(rows[14])

    mo = re.match('^([A-Z]+)-([A-Z]+)$', rows[1])
    if mo is None:
        raise RuntimeError('malformed currency pair: ' + rows[1])
    quote = coinname(mo.group(2))
    base  = coinname(mo.group(1))

    r_quote = cctaxjp.Record(dt, 'Bittrex', rid, cctaxjp.RecordType.EXCHANGE, quote, Decimal(rows[5]) - Decimal(rows[6]))
    r_base  = cctaxjp.Record(dt, 'Bittrex', rid, cctaxjp.RecordType.EXCHANGE, base, rows[8], exfee="-"+rows[7])
    if rows[3] == 'LIMIT_BUY':
        r_base.amount = -r_base.amount
    elif rows[3] == 'LIMIT_SELL':
        r_quote.amount = -r_quote.amount
    else:
        raise RuntimeError('unknown OrderType: ' + rows[3])
    records = [ r_quote, r_base ] if 0 <= r_quote.amount else [ r_base, r_quote ]
    return records, ctx

def get_normalizer(header):
    if header == 'Uuid,Exchange,TimeStamp,OrderType,Limit,Quantity,QuantityRemaining,Commission,Price,PricePerUnit,IsConditional,Condition,ConditionTarget,ImmediateOrCancel,Closed,TimeInForceTypeId,TimeInForce':
        return norm_order
    if header == 'OrderUuid,Exchange,Type,Quantity,Limit,CommissionPaid,Price,Opened,Closed':
        return norm_old_order
    else:
        return None

