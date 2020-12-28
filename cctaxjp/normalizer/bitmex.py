#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+" +0000", "%Y/%m/%d %H:%M:%S %z")
def parse_execType(s):
    if s == 'Trade':
        return cctaxjp.RecordType.EXCHANGE
    elif s == 'Funding':
        return cctaxjp.RecordType.FUNDING
    else:
        raise RuntimeError("unknown execType: " + s)

COINNAME_MAP = {
    'USD': cctaxjp.CoinName.USD,
    'USDT': cctaxjp.CoinName.USDT,
    'XBT': cctaxjp.CoinName.BTC,
    'ADA': cctaxjp.CoinName.ADA,
    'BCH': cctaxjp.CoinName.BCH,
    'BNB': cctaxjp.CoinName.BNB,
    'DOT': cctaxjp.CoinName.DOT,
    'EOS': cctaxjp.CoinName.EOS,
    'ETH': cctaxjp.CoinName.ETH,
    'LINK': cctaxjp.CoinName.LINK,
    'LTC': cctaxjp.CoinName.LTC,
    'TRX': cctaxjp.CoinName.TRX,
    'XRP': cctaxjp.CoinName.XRP,
    'XTZ': cctaxjp.CoinName.XTZ,
    'YFI': cctaxjp.CoinName.YFI,
}
def parse_symbol(s0):
    keys = COINNAME_MAP.keys()
    quote, base = None, None
    s = s0
    for k in keys:
        if s.startsWith(k):
            quote = k
            break
    if quote is None:
        raise RuntimeError("unknown quote of symbol: " + s0)
    else:
        s = s[len(quote):]
    for k in keys:
        if s.startsWith(k):
            base = k
            break
    if base is None:
        base = 'XBT'
    else:
        s = s[len(base):]
    if s != '' and re.match('^[A-Z][0-9]+$', s) is None:
        raise RuntimeError("unknown suffix of symbol: " + s0)
    return (COINNAME_MAP[quote], COINNAME_MAP[base])

"""
  0 "transactTime" -> 時間

  1 "symbol" -> 記号.
    <quote><base> か、<quote>[base]<先物長>。
    <quote> は3文字とは限らんようで、決め打ちで調べるしかなさげ。
    XBT,ADA,BCH,BNB,DOT,EOS,ETH,LINK,LTC,TRX,XRP,XTZ,YFI
    base 通貨省略時は XBT のようだ。
    期間は Z20, H21, M21

  2 "execType" -> 執行タイプ
  3 "side" -> サイド. Trade だと Sell/Buy, Funding だと空みたい。

  4 "lastQty" -> 執行数量
    base 通貨単位。

  5 "lastPx" -> 執行価格
    base 通貨単位。

  6 "execCost" -> 値
    レバレッジで実際に担保に使う分?
    base に依らず、satoshi 単位のようだ。

  7 "commission" -> 手数料
    割合。プラス有り。

  8 "execComm" -> 支払済み手数料
    execCost * commision みたい。つまり satoshi 単位。少数第一位以下切り捨てかな。

  9 "ordType" -> 注文タイプ
 10 "orderQty" -> 注文数量
 11 "leavesQty" -> 残数量
 12 "price" -> 注文価格
 13 "text" -> 文章
 14 "orderID" -> 注文ID
"""
def norm_trade(rows, ctx, opts):
    # "transactTime","symbol","execType","side","lastQty","lastPx","execCost","commission","execComm","ordType","orderQty","leavesQty","price","text","orderID"
    rid = rows[14]
    dt = parse_datetime(rows[0])
    quote, base = parse_symbol(rows[1])

    rtype = parse_execType(rows[2])
    r_quote = cctaxjp.Record(dt, 'Bittrex', rid, rtype, quote, rows[6])
    r_base  = cctaxjp.Record(dt, 'Bittrex', rid, rtype, base, rows[6])
    r_fee   = cctaxjp.Record(dt, 'Bittrex', rid, cctaxjp.RecordType.EXFEE, cctaxjp.RecordType.BTC, rows[8] * Decimal('1e-8'))
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
    if header == '"transactTime","symbol","execType","side","lastQty","lastPx","execCost","commission","execComm","ordType","orderQty","leavesQty","price","text","orderID"':
        return norm_trade
    elif header == "transactTime","transactType","amount","fee","address","transactStatus","walletBalance":
        return norm_wallet
    else:
        return None

