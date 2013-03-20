#!/usr/bin/env node

var sys = require('sys'),
    log = require('logging'),
    program = require('commander'),
    exec = require('child_process').exec;

program
    .version('0.0.1')
    .usage('./text_to_speech <"sentence">')
    .description('Command line vocal synthetizer, powerd by google')
    .option('-t, --text <text>', 'Text to synthetize', String, '')
    .option('-l, --lang <lang>', 'Short language code to synthetize', String, 'en')
    .option('-e, --encoding <code>', 'Text encoding', String, 'utf-8')
    .parse(process.argv);

function puts(error, stdout, stderr) { sys.puts(stdout) }

function synthetize(text, lang, encoding) {
    log('Setup default parameters')
    lang = lang || 'en';
    encoding = encoding || 'UTF-8';

    log('Constructing google speech api request')
    request = 'http://translate.google.com/translate_tts?ie=' + encoding + '&tl=' + lang + '&q=' + text.replace(/ /g, '+');

    log('Using mplayer program to play mp3 received')
    //exec('mplayer "' + request + '" > /dev/null', puts);
    child = exec('mplayer "' + request + '" > /dev/null', function(error, stdout, stderr) {
        log('[Stdout] ' + stdout);
        log('[Stderr] ' + stderr);
        if (error !== null) {
            log('** Exec error: ' + error);
        }
    });

    log('Done')
}

log('Synthetizing "' + program.text + '" in ' + program.lang + ' (' + program.encoding + ')')
synthetize(program.text, program.lang, program.encoding);
