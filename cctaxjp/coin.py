#!/usr/bin/env python
# -*- coding: utf-8 -*-

class CoinName:
    # fiat
    USD = 'USD'
    USDT = 'USDT'
    JPY = 'JPY'

    # minor
    ADA = 'ADA'
    ADX = 'ADX'
    ARDR = 'ARDR'
    ARK = 'ARK'
    BAT = 'BAT'
    BCH = 'BCH'
    BCN = 'BCN'
    BNB = 'BNB'
    BTC = 'BTC'
    BTG = 'BTG'
    BTS = 'BTS'
    BTT = 'BTT'
    CANN = 'CANN'
    CMT = 'CMT'
    CVC = 'CVC'
    DASH = 'DASH'
    DCT = 'DCT'
    DNT = 'DNT'
    DGB = 'DGB'
    DOGE = 'DOGE'
    EDG = 'EDG'
    ELF = 'ELF'
    ETC = 'ETC'
    ETH = 'ETH'
    FCT = 'FCT'
    GAME = 'GAME'
    GBYTE = 'GBYTE'
    GEO = 'GEO'
    GNO = 'GNO'
    GNT = 'GNT'
    IOTA = 'IOTA'
    KMD = 'KMD'
    LBC = 'LBC'
    LSK = 'LSK'
    LTC = 'LTC'
    MONA = 'MONA'
    MTL = 'MTL'
    NEO = 'NEO'
    NMR = 'NMR'
    NXT = 'NXT'
    OK = 'OK'
    OMG = 'OMG'
    ONT = 'ONT'
    PAY = 'PAY'
    PIVX = 'PIVX'
    PTOY = 'PTOY'
    QTUM = 'QTUM'
    RDD = 'RDD'
    RISE = 'RISE'
    SAFEX = 'SAFEX'
    SC = 'SC'
    SNT = 'SNT'
    SRN = 'SRN'
    STORJ = 'STORJ'
    STR = 'STR'
    STRAX = 'STRAX'
    TKN = 'TKN'
    TRIG = 'TRIG'
    VTC = 'VTC'
    WAVES = 'WAVES'
    XEM = 'XEM'
    XLM = 'XLM'
    XMR = 'XMR'
    XRP = 'XRP'
    XST = 'XST'
    XVG = 'XVG'
    ZEC = 'ZEC'
    ZRX = 'ZRX'

    @classmethod
    def check_value(cls, x):
        if x in vars(cls).values():
            return x
        else:
            raise ValueError("{} is not defined in CoinName".format(x))

#if __name__ == '__main__':