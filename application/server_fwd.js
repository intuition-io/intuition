#!/usr/bin/env node
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

/*
 * This module is a bridge between a remote server and the client
 * It uses 0MQ to dispatch bi-directionnal messages to clients according to the channel parameter
 * In addition it can run local program (with futur cluster module, one per core actually)
 * FIXME Prevent him from stopping (forever module ?)
 */


var log     = require('logging'),
    program = require('commander'),
    config  = require('config'),
    messenger = require('../server/messenger');
    
program
    .version('0.0.3')
    .usage('[commands] <args>')
    .description('Forwarder interface for NeuronQuant trading system, server part')
    .option('-v , --verbose <level>' , 'verbosity'            , Number , 2)
    .option('-b , --backend <uri>'   , 'Backend port adress'  , String , config.network.backport)
    .option('-f , --frontend <uri>'  , 'Frontend port adress' , String , config.network.frontport)
    .option('-l , --logger <uri>'    , 'Logger port adress'   , String , config.network.logger)
    .parse(process.argv);

log('Running Broker device.')
messenger.create_queue_device(program.frontend, program.backend, program.logger);
