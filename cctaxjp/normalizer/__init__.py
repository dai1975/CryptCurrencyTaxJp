# -*- coding: utf-8 -*-

import cctaxjp
import importlib

NORMALIZERS = [
    'binance',
]

def normalize(typ, with_header, debug, files):
    m = importlib.import_module('cctaxjp.normalizer.%s' % typ)
    opts = {
        'with_header': with_header,
        'debug': debug,
    }
    if opts['with_header']: print(cctaxjp.Record.header())
    for f in files:
        m.normalize(f, opts)


