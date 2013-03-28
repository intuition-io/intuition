//
// Copyright 2012 Xavier Bruhiere
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.


var sys = require('sys'),
    exec = require('child_process').exec;

function puts(error, stdout, stderr) { sys.puts(stdout) }

exports.synthetize = function(text, lang, encoding) {
    // Default parameters
    lang = lang || 'en';
    encoding = encoding || 'UTF-8';

    // Constructing google speech api request
    request = 'http://translate.google.com/translate_tts?ie=' + encoding + '&tl=' + lang + '&q=' + text.replace(/ /g, '+');

    // Using mplayer program to play mp3 received
    exec('mplayer "' + request + '" > /dev/null', puts);
}

/*
 * Usage: 
 * synthetize('Hi Xavier, you just received a new mail. You should take a look !', 'en');
 */
