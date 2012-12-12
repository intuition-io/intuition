#!/usr/bin/python
# -*- coding: utf8 -*-

import sys
sys.path.append('../pocoVersion/pyTrade')
from data.QuotesFetcher import QuotesDL

from datetime import datetime

def init():
    return QuotesDL('google', '../pocoVersion/dataSubSystem/assets.db')
