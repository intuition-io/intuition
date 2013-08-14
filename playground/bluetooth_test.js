var btSerial = new (require('bluetooth-serial-port')).BluetoothSerialPort();

btSerial.on('found', function(address, name) {
    btSerial.findSerialPortChannel(address, function(channel) {
        console.log('Device ' + name + ' found, ' + address + ':' + channel)
        btSerial.connect(address, channel, function() {
            console.log('connected');

            //btSerial.write('my data');

            btSerial.on('data', function(data) {
                console.log(data);
            });
        }, function () {
            console.log('cannot connect');
        });

        // close the connection when you're ready
        btSerial.close();       
    });
});

btSerial.inquire();
