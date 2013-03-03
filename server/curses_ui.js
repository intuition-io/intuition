var lazy_prgm = require('sleep');
var nc = require('ncurses');

function getTimestamp() {
	var time = new Date();
	var hours = time.getHours();
	var mins = time.getMinutes();
	return "" + (hours < 10 ? "0" : "") + hours + ":" + (mins < 10 ? "0" : "") + mins;
}

exports.UI_interface = function(command_cb) {
    var stdscr = new nc.Window(),
        msg_w = new nc.Window(Math.round(stdscr.height/3), stdscr.width - 10, 5, 5),
        log_w = new nc.Window(Math.round(stdscr.height/3), stdscr.width - 10, Math.round(msg_w.height + 10), 5),
        callback = command_cb;

    log_w.on('inputChar', function(ch, ch_code) {
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
            //appendLine(msg_w, stdscr.inbuffer);
            callback(stdscr.inbuffer);
            stdscr.inbuffer = '';
            stdscr.cursor(stdscr.height-2, 16);
            stdscr.clrtoeol();
        }
        else if (ch_code >= 32 && ch_code <= 126) {
            stdscr.echochar(ch_code);
            stdscr.inbuffer += ch;
        }
        nc.redraw();
    });

    this.appendLine = function(win, message, attrs) {
        var curx = win.curx,
            cury = win.cury,
            time = getTimestamp();
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
    this.setup_window = function(win, title) {
        if (title)
            win.frame(title);
        win.scrollok(true);
        win.setscrreg(1, win.height);
    }

    this.setup_canvas = function(title) {
        nc.showCursor = false;
        stdscr.hline(stdscr.height - 3, 0, stdscr.width);
        if (title)
            stdscr.frame(title);
        stdscr.print(stdscr.height-2, 2, 'NeuronQuant > ')
        nc.redraw();
        stdscr.inbuffer = "";
    }

    this.write_log = function(msg) {
        this.appendLine(log_w, msg);
    }

    this.write_msg = function(msg) {
        this.appendLine(msg_w, msg);
    }

    this.setup_canvas('  Dev Console  ');
    this.setup_window(msg_w);
    this.setup_window(log_w);
    //ui.setup_event(ui.log_w)
}

/*
 *function callback(msg) {
 *    console.log(msg);
 *}
 *
 *
 * Usage:
 *var ui = new UI_interface();
 *
 *for (var i = 0; i < 20; i += 1) {
 *    ui.write_log('pouet bla bla blaaaaaaaaaaaaaaaaaaaaaaaaaaaavvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa');
 *    ui.write_msg('pouet bla bla blaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaffffffffffffffffffffffffffffffffffffffaaaaaaaa');
 *}
 */
