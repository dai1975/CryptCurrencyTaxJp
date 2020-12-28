# -*- coding: utf-8 -*-

import traceback
import importlib
import csv
import cctaxjp

IN_MODULES = [
    'custom', 'bittrex', 'binance', 'bitfinex', 'poloniex', 'etherscan',
]
OUT_MODULES = [
    'gtax',
]

in_modules = [ importlib.import_module('cctaxjp.normalizer.%s' % m) for m in IN_MODULES ]
out_modules = { m: importlib.import_module('cctaxjp.normalizer.%s' % m) for m in OUT_MODULES }

def get_formatter(of):
    if of == None:
        h = lambda: cctaxjp.Record.header()
        f = lambda r: r.format()
        return (h,f)
    else:
        m = out_modules[of]
        return (m.header, m.format)

def normalize(out_format, with_header, debug, files):
    opts = {
        'with_header': with_header,
        'debug': debug,
    }
    formatter = get_formatter(out_format)
    if opts['with_header'] or formatter is not None: print(formatter[0]())
    for f in files:
        header = f.readline().rstrip("\r\n")
        func = None
        if header == '': continue
        for m in in_modules:
            func = m.get_normalizer(header)
            if func is not None: break
        if func is None:
            print(header)
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
                    print(formatter[1](r))
            except Exception as e:
                logger("ERROR: " + str(e))
                raise
