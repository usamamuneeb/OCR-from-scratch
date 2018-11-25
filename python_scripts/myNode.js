
var spawn = require('child_process').spawn,
    py    = spawn('python', ['myLayout.py', '--filename', 'post_skew', '--ext', 'png']),
    dataString = '';

py.stdout.on('data', function(data) {
    receivedData = data.toString()
    console.log(receivedData)
    dataString += receivedData;
});

py.stdout.on('end', function() {
    console.log(dataString);
});
