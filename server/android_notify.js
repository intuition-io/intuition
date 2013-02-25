//TODO Parse return message http://www.notifymyandroid.com/api.jsp#returnmsg
var xml = require('xml2js');
var request = require('request');
exports.apikey = process.env.QTRADE_NMA_KEY;

// send a notification command to your device:
//notifyMA(apikey, "News Crow", "Winter is Coming!", "It's been -4C degrees here, so Winter is coming for sure!", 4 );
//checkMAKey(apikey)
 
exports.notify = function(keystring, appname, eventtitle, descriptiontext, priorityvalue) {
  // you can also use (http|https).request but this was easier for me
  var r = request.post('http://www.notifymyandroid.com/publicapi/notify', {form : {apikey: keystring,
                     application: appname,
                     event: eventtitle,
                     description: descriptiontext,
                     priority: priorityvalue}}, function (error, response, body) {
        if (!error) {
            if (response.statusCode == 200) {
                var parser = new xml.Parser()
                parser.parseString(body.toString(), function(err, result){
                    var success = result.nma.success[0].$;
                    // you can use these to manage your notification cases
                    console.log("Notifications has been sent successfully: " + success.code);
                    console.log("\tRemaining  : " + success.remaining);
                    console.log("\tResettimer : " + success.resettimer);
                });
            }
            else {
                var parser = new xml.Parser()
                parser.parseString(body.toString(), function(err, result) {
                    var error = result.nma.error[0].$;
                    console.log(error.code + ': Invalid key - ' + keystring);
                    console.log(error._)
                    if (error.code == 402) {
                        console.log(error.timeleft + ' minutes left before hour limit reset')
                    }
                })
            }
        }
        else {
            console.log('** Error in get request')
        }
    });
}

exports.check_key = function(keystring) {
    check_url = 'https://www.notifymyandroid.com/publicapi/verify';
    var r_code = request.get(check_url, {qs: {apikey: keystring}}, function(error, response, body) {
        console.dir(body)
        if (!error) {
            if (response.statusCode == 200) {
                var parser = new xml.Parser()
                parser.parseString(body.toString(), function(err, result) {
                    var success = result.nma.success[0].$;
                    // you can use these to manage your notification cases
                    console.log('The apikey supplied is valid - ' + keystring);
                    console.log("\tRemaining  : " + success.remaining);
                    console.log("\tResettimer : " + success.resettimer);
                //console.log()
                })
            }
            else {
                var parser = new xml.Parser()
                parser.parseString(body.toString(), function(err, result) {
                    var error = result.nma.error[0].$;
                    console.log(error.code + ': Invalid key - ' + keystring);
                    console.log(error._)
                    if (error.code == 402) {
                        console.log(error.timeleft + ' minutes left before hour limit reset')
                    }
                })
            }
        } 
        else {
            console.log('** Error sending notification.')
        }
    })
}
