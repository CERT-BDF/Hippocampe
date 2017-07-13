#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import imap, groupby
from operator import itemgetter
from re import compile
from netaddr import IPNetwork

CIDR_re = compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$')

def unique_justseen(iterable, key=None):
    "List unique elements, preserving order. Remember only the element just seen."
    # unique_justseen('AAAABBBCCDAABBB') --> A B C D A B
    # unique_justseen('ABBCcAD', str.lower) --> A B C A D
    return imap(next, imap(itemgetter(1), groupby(iterable, key)))

def transform_cidr(iterable, key=None):
    iterable_transformed = []

    for dict in iterable:
        if CIDR_re.match(dict.get(key)):
            for ip in IPNetwork(dict.get(key)):
                dict['ip'] = str(ip)
                iterable_transformed.append(dict)
        else:
            iterable_transformed.append(dict)

    return iterable_transformed
