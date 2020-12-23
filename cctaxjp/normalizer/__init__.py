# -*- coding: utf-8 -*-

import traceback
import importlib
import csv
import cctaxjp

MODULES = [
    'custom', 'bittrex', 'binance', 'bitfinex', 'poloniex'
]

modules = [ importlib.import_module('cctaxjp.normalizer.%s' % m) for m in MODULES ]

def normalize(with_header, debug, files):
    opts = {
        'with_header': with_header,
        'debug': debug,
    }
    if opts['with_header']: print(cctaxjp.Record.header())
    for f in files:
        header = f.readline().rstrip("\r\n")
        func = None
        if header == '': continue
        for m in modules:
            func = m.get_normalizer(header)
            if func is not None: break
        if func is None:
            raise RuntimeError("cannot detect format of file: " + f.name)
        line = 1
        ctx = None
        for rows in csv.reader(f):
            line += 1
            if len(rows) == 0: continue

            logger = lambda s: print("{} at line {} in {}".format(s, f.name, line))
            try:
                records, ctx = func(rows, ctx, dict({ "logger":logger, "filename":f.name, "line":line }, **opts))
                for r in records:
                    print(r.format())
            except Exception as e:
                logger("ERROR: " + str(e))
                raise

