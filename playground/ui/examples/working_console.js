var lazy_prgm = require('sleep');
var nc = require('ncurses');

var stdscr = new nc.Window(),
    msg_w = new nc.Window(Math.round(stdscr.height/3), stdscr.width - 10, 5, 5),
    log_w = new nc.Window(Math.round(stdscr.height/3), stdscr.width - 10, Math.round(msg_w.height + 10), 5),
    tmo;


function setup_event(win) {
    win.on('inputChar', function(ch, ch_code) {
        if (ch_code == nc.keys.ESC) {
            nc.cleanup();
            process.exit(0);
        } 
        else if (ch_code == nc.keys.NEWLINE) {
            if (stdscr.inbuffer.length) {
                if (stdscr.inbuffer == 'exit') {
                    nc.cleanup();
                    process.exit(0);
                }
            }
            appendLine(msg_w, stdscr.inbuffer);
            stdscr.inbuffer = '';
            stdscr.cursor(stdscr.height-2, 16);
            stdscr.clrtoeol();
        }
        else if (ch_code >= 32 && ch_code <= 126) {
            stdscr.echochar(ch_code);
            stdscr.inbuffer += ch;
        }
        nc.redraw();
        clearTimeout(tmo);
    });
}

function setup_window(win, title) {
    if (title)
        win.frame(title);
    win.scrollok(true);
    win.setscrreg(1, win.height);
}

function setup_canvas(title) {
    nc.showCursor = false;
    stdscr.hline(stdscr.height - 3, 0, stdscr.width);
    if (title)
        stdscr.frame(title);
    stdscr.print(stdscr.height-2, 2, 'NeuronQuant > ')
    nc.redraw();
    stdscr.inbuffer = "";
}


setup_canvas('  Dev Console  ');
setup_window(msg_w);
setup_window(log_w);
setup_event(log_w)

for (var i = 0; i < 20; i += 1) {
    appendLine(log_w, 'pouet bla bla blaaaaaaaaaaaaaaaaaaaaaaaaaaaavvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa');
    appendLine(msg_w, 'pouet bla bla blaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaffffffffffffffffffffffffffffffffffffffaaaaaaaa');
    //lazy_prgm.sleep(1);
    nc.redraw()
}

tmo = setTimeout(function() { stdscr.close(); }, 5000);

function appendLine(win, message, attrs) {
	var curx = win.curx, cury = win.cury, time = getTimestamp();
	win.scroll(1);
	win.cursor(win.height-4, 0);
	win.print("[" + time + "] ");
	if (attrs)
	  win.attron(attrs);
	win.print(message);
	if (attrs)
	  win.attroff(attrs);
	win.cursor(cury, curx);
	win.refresh();
}

function getTimestamp() {
	var time = new Date();
	var hours = time.getHours();
	var mins = time.getMinutes();
	return "" + (hours < 10 ? "0" : "") + hours + ":" + (mins < 10 ? "0" : "") + mins;
}

process.on('uncaughtException', function (err) {
    nc.cleanup()
    console.error('[Node:worker] An uncaught error occurred!');
    console.error(err.stack);
    process.exit(0)
});
