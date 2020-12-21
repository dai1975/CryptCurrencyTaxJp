#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import cctaxjp

def normalize(args):
    cctaxjp.normalize(args.format, args.header, args.debug, args.files)
def balance(args):
    cctaxjp.calc_balance(args.file)

p = argparse.ArgumentParser()
sp = p.add_subparsers(required=True)

p1 = sp.add_parser("normalize", aliases=["n"])
p1.add_argument('-f', '--format', dest="format", required=True, choices=cctaxjp.NORMALIZERS)
p1.add_argument('--with-header', dest="header", action='store_true')
p1.add_argument('--debug', dest="debug", action='store_true')
p1.add_argument('files', nargs='+', type=argparse.FileType('r', encoding='UTF-8'))
p1.set_defaults(func=normalize)

p2 = sp.add_parser("balance", aliases=["b"])
p2.add_argument('--debug', dest="debug", action='store_true')
p2.add_argument('file', nargs='?', type=argparse.FileType('r', encoding='UTF-8'))
p2.set_defaults(func=balance)

args = p.parse_args()
args.func(args)





