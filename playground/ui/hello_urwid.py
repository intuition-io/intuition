# http://www.nicosphere.net/selectable-list-with-urwid-for-python-2542/
import urwid

txt = urwid.Text("Hello World")
fill = urwid.Filler(txt, 'top')

def exit(input):
    if input in ('q', 'Q'):
        raise urwid.ExitMainLoop()

loop = urwid.MainLoop(fill, unhandled_input=exit)
loop.run()
