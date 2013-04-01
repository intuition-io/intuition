var Imap = require('imap'),
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
  console.log('Uh oh: ' + err);
  process.exit(1);
}

function openInbox(cb) {
  imap.connect(function(err) {
    if (err) die(err);
    imap.openBox('INBOX', true, cb);
  });
}

var fs = require('fs'), fileStream;

openInbox(function(err, mailbox) {
  if (err) die(err);
  imap.search([ 'UNSEEN', ['SINCE', 'May 20, 2012'] ], function(err, results) {
    if (err) die(err);
    imap.fetch(results,
      { headers: { parse: false },
        body: true,
        cb: function(fetch) {
          fetch.on('message', function(msg) {
            console.log('Got a message with sequence number ' + msg.seqno);
            fileStream = fs.createWriteStream('msg-' + msg.seqno + '-body.txt');
            msg.on('data', function(chunk) {
              fileStream.write(chunk);
            });
            msg.on('end', function() {
              fileStream.end();
              console.log('Finished message no. ' + msg.seqno);
            });
          });
        }
      }, function(err) {
      }
    );
  });
});
