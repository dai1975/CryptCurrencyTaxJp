#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import cctaxjp

def norm_custom(rows, ctx, opts):
    # datetime,currency,amount,infee,exfee,custom comment
    # 2020-02-28,MikuExchange,DEPOSIT,BTC,0.939393939,example data
    dt = datetime.strptime(rows[0], "%Y-%m-%d %H:%M:%S%z")
    rtype = cctaxjp.RecordType.check_value(rows[2])
    coin = cctaxjp.CoinName.check_value(rows[3])
    r = cctaxjp.Record(dt, rows[1], None, rtype, coin, rows[4], infee=rows[5], exfee=rows[6])
    return [r],ctx

def get_normalizer(header):
    if header == 'datetime,source,type,currency,amount,infee,exfee,custom comment':
        return norm_custom
    else:
        return None

