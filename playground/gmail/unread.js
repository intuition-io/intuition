//https://github.com/mscdex/node-imap
//extra stuff: https://github.com/andris9/mimelib
//parsing: https://github.com/andris9/mailparser

var Imap = require('imap'),
    log = require('logging'),
    inspect = require('util').inspect;

var imap = new Imap({
      user: 'xavier.bruhiere@gmail.com',
      password: '',
      host: 'imap.gmail.com',
      port: 993,
      secure: true
    });

function show(obj) {
  return inspect(obj, false, Infinity);
}

function die(err) {
  log('Uh oh: ' + err);
  process.exit(1);
}

function openInbox(cb) {
  imap.connect(function(err) {
    if (err) die(err);
    imap.openBox('INBOX', true, cb);
  });
}

openInbox(function(err, mailbox) {
  if (err) die(err);
  imap.search([ 'UNSEEN', ['SINCE', 'May 20, 2012'] ], function(err, results) {
    if (err) die(err);
    imap.fetch(results,
      { headers: ['from', 'to', 'subject', 'date'],
        cb: function(fetch) {
          fetch.on('message', function(msg) {
            log('Saw message no. ' + msg.seqno);

            msg.on('headers', function(hdrs) {
              log('Headers for no. ' + msg.seqno + ': ' + show(hdrs));
            });

            msg.on('end', function() {
              log('Finished message no. ' + msg.seqno);
            });
          });
        }
      }, function(err) {
        if (err) throw err;
        log('Done fetching all messages!');
        imap.logout();
      }
    );
  });
});
