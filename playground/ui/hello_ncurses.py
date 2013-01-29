#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import curses.wrapper


def test(window):
    pad = curses.newpad(100, 100)
    for y in range(0, 100):
        for x in range(0, 100):
            try:
                pad.addch(y, x, ord('a') + (x * x + y * y) % 26)
            except curses.error:
                pass

    #  Displays a section of the pad in the middle of the screen
    pad.refresh(0, 0, 5, 5, 20, 75)
    import time
    time.sleep(4)

if __name__ == '__main__':
    curses.wrapper(test)
