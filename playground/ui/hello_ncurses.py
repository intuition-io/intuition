#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import curses.wrapper
import time


def test(window):
    #pad = curses.newpad(200, 200)
    win = curses.newwin(10, 40, 5, 5)
    log_win = curses.newwin(10, 80, 5, 40)
    win.border(0)
    for y in range(0, 10):
        for x in range(0, 40):
            try:
                win.addch(y, x, ord('a') + (x * x + y * y) % 26)
                log_win.addch(y, x, ord('a') + (x * x + y * y) % 26)
                win.refresh()
                log_win.refresh()
                time.sleep(0.05)
            except curses.error:
                pass

    '''
    for y in range(0, 100):
        for x in range(0, 100):
            #  Displays a section of the pad in the middle of the screen
            pad.refresh(0, 0, 5 + y, 5 + x, 20, 75)
            time.sleep(0.1)
    '''
    c = win.getch()
    print c

if __name__ == '__main__':
    curses.wrapper(test)
