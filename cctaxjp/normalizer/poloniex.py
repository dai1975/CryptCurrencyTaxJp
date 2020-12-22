#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import csv
from datetime import datetime
from decimal import Decimal, ROUND_DOWN
import cctaxjp

def parse_datetime(s):
    return datetime.strptime(s+"+0000", "%Y-%m-%d %H:%M:%S%z")

class CoinInfo:
    def __init__(self, local_name, general_name, rank):
        self.local_name = local_name
        self.general_name = general_name
        self.rank = rank
COINS = {
    "USDT": CoinInfo('USDT', cctaxjp.CoinName.USDT, 0),
    "BTC": CoinInfo('BTC', cctaxjp.CoinName.BTC, 1),
    "BCH": CoinInfo('BCH', cctaxjp.CoinName.BCH, 2),
    "ETH": CoinInfo('ETH', cctaxjp.CoinName.ETH, 2),
    "ETC": CoinInfo('ETC', cctaxjp.CoinName.ETC, 2),
    "DOGE": CoinInfo('DOGE', cctaxjp.CoinName.DOGE, 2),
    "LTC": CoinInfo('LTC', cctaxjp.CoinName.LTC, 2),
    "XRP": CoinInfo('XRP', cctaxjp.CoinName.XRP, 100),
    "XEM": CoinInfo('XEM', cctaxjp.CoinName.XEM, 100),
    "ARDR": CoinInfo('ARDR', cctaxjp.CoinName.ARDR, 100),
    "GNT": CoinInfo('GNT', cctaxjp.CoinName.GNT, 100),
    "DASH": CoinInfo('DASH', cctaxjp.CoinName.DASH, 100),
    "BCN": CoinInfo('BCN', cctaxjp.CoinName.BCN, 100),
    "LSK": CoinInfo('LSK', cctaxjp.CoinName.LSK, 100),
    "DGB": CoinInfo('DGB', cctaxjp.CoinName.DGB, 100),
    "BTS": CoinInfo('BTS', cctaxjp.CoinName.BTS, 100),
    "FCT": CoinInfo('FCT', cctaxjp.CoinName.FCT, 100),
    "STR": CoinInfo('STR', cctaxjp.CoinName.STR, 100),
    "NXT": CoinInfo('NXT', cctaxjp.CoinName.NXT, 100),
    "XMR": CoinInfo('XMR', cctaxjp.CoinName.XMR, 100),
    "SC": CoinInfo('SC', cctaxjp.CoinName.SC, 100),
    "GAME": CoinInfo('GAME', cctaxjp.CoinName.GAME, 100),
    "ZEC": CoinInfo('ZEC', cctaxjp.CoinName.ZEC, 100),
    "ZRX": CoinInfo('ZRX', cctaxjp.CoinName.ZRX, 100),
    "GNO": CoinInfo('GNO', cctaxjp.CoinName.GNO, 100),
    "BTT": CoinInfo('BTT', cctaxjp.CoinName.BTT, 100),
}

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
def norm_trade(rows):
    # Date,Market,Category,Type,Price,Amount,Total,Fee,Order Number,Base Total Less Fee,Quote Total Less Fee,Fee Currency,Fee Total
    # 2017-03-09 00:11:22,BTC/USDT,Exchange,Buy,8064.00000000,0.11359561,916.03499904,0.25%,111641538829,-916.03499904,0.11331162,BTC,2.29008749
    dt = parse_datetime(rows[0])
    mo = re.match('^([A-Z]+)\/([A-Z]+)$', rows[1])
    if mo is None:
        raise RuntimeError('unknown currency pair: ' + rows[1])
    quote, base = mo.group(1), mo.group(2)

    mo = re.match('^([0-9]*(\.[0-9]*)?)\%$', rows[7])
    if mo is None:
        raise RuntimeError('malformed fee value: ' + rows[7])
    fee_rate = Decimal(mo.group(1)) / 100

    r_quote = cctaxjp.Record(dt, 'Poloniex', rows[8], cctaxjp.RecordType.EXCHANGE, COINS[quote].general_name)
    r_base  = cctaxjp.Record(dt, 'Poloniex', rows[8], cctaxjp.RecordType.EXCHANGE, COINS[base].general_name)
    if rows[3] == 'Buy':
        r_quote.amount = Decimal(rows[5])
        r_base.amount  = -Decimal(rows[6])
        r_quote.exfee = -(r_quote.amount * fee_rate).quantize(Decimal('1.0E-7'), ROUND_DOWN)
    else:
        r_quote.amount = -Decimal(rows[5])
        r_base.amount  = Decimal(rows[6])
        r_base.exfee   = -(r_base.amount * fee_rate).quantize(Decimal('1.0E-7'), ROUND_DOWN)
    return [ r_quote, r_base ] if 0 <= r_quote.amount else [ r_base, r_quote ]

def norm_distribution(rows):
    # date,currency,amount,wallet
    # 2020-02-28,BTT,500.00000000,exchange
    dt = parse_datetime(rows[0] + ' 00:00:00')
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.AIRDROP, COINS[rows[1]].general_name, rows[2])
    return [r]

def norm_lending(rows):
    # Currency,Rate,Amount,Duration,Interest,Fee,Earned,Open,Close
    # BTC,0.00008100,0.00131978,2.00032407,0.00000021,-0.00000003,0.00000018,2020-03-09 05:41:17,2020-03-11 05:41:45
    dt = parse_datetime(rows[8])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.LENDING, COINS[rows[0]].general_name, rows[4], exfee=rows[5])
    return [r]

def norm_deposit(rows):
    # Date,Currency,Amount,Address,Status
    # 2017-03-09 11:22:33,ZEC,0.00046672,t1ZYy...,COMPLETE
    dt = parse_datetime(rows[0])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.DEPOSIT, COINS[rows[1]].general_name, rows[2])
    return [r]

def norm_withdrawal(rows):
    # Date,Currency,Amount,Fee Deducted,Amount - Fee,Address,Status
    # 2017-03-09 11:22:33,BTC,0.20000000,0.00050000,0.1995,3FZQ...,COMPLETE: 7092...
    dt = parse_datetime(rows[0])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.WITHDRAWAL, COINS[rows[1]].general_name, "-"+rows[2], infee="-"+rows[3])
    return [r]

def norm_margin_borrowing(rows):
    # Currency,Rate,Amount,Duration,TotalFee,Open,Close
    raise RuntimeError("not implemented yet")

def norm_custom(rows):
    # datetime,currency,amount,CUSTOM
    dt = parse_datetime(rows[0])
    r = cctaxjp.Record(dt, 'Poloniex', None, cctaxjp.RecordType.ADJUST, COINS[rows[1]].general_name, rows[2])
    return [r]

def normalize(f, opts):
    reader = csv.reader(f)
    pairs = []
    line = 0
    func = None
    for rows in reader:
        line += 1
        if len(rows) == 0: continue
        if line == 1:
            l = ",".join(rows)
            if l == 'Date,Market,Category,Type,Price,Amount,Total,Fee,Order Number,Base Total Less Fee,Quote Total Less Fee,Fee Currency,Fee Total':
                func = norm_trade
            elif l == 'date,currency,amount,wallet':
                func = norm_distribution
            elif l == 'Currency,Rate,Amount,Duration,Interest,Fee,Earned,Open,Close':
                func = norm_lending
            elif l == 'Date,Currency,Amount,Address,Status':
                func = norm_deposit
            elif l == 'Date,Currency,Amount,Fee Deducted,Amount - Fee,Address,Status':
                func = norm_withdrawal
            elif l == 'Currency,Rate,Amount,Duration,TotalFee,Open,Close':
                func = norm_margin_borrowing
            elif l == 'datetime,currency,amount,CUSTOM':
                func = norm_custom
            else:
                raise RuntimeError("unknown file type: " + l)
            continue
        for r in func(rows):
            print(r.format())

#if __name__ == '__main__':
