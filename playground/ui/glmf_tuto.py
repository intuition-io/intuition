import curses
import time


def init_curses():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    return stdscr


def close_curses(stdscr):
    stdscr.keypad(0)
    curses.nocbreak()
    curses.echo()
    curses.endwin()


def init_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

if __name__ == '__main__':
    try:
        stdscr = init_curses()
        init_colors()

        main_window = stdscr.subwin(40, 30, 3, 5)
        main_window.border(0)

        main_window.addstr(1, 1, 'red msg', curses.A_BOLD | curses.color_pair(1))

        main_window.refresh()

        log_pad = curses.newpad(100, 100)
        for y in range(0, 100):
            for x in range(0, 100):
                try:
                    log_pad.addch(y, x, ord('a') + (x * x + y * y) % 26)
                except curses.error:
                    pass

        for j in range(5):
            for i in range(5):
                time.sleep(0.5)
                log_pad.refresh(0 + 2 * i, 0 + 2 * j, 5, 5, 20, 75)

        c = main_window.getch()

    finally:
        close_curses(stdscr)
