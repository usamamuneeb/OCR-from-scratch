const fs = require('fs')
const formidable = require('formidable')
const http = require('http')
const socketio = require('socket.io')
const gm = require('gm')
const PDFDocument = require('pdfkit')

var readline = require('readline')
var stream = require('stream')


var fonts = {
	Roboto: {
		normal: 'fonts/Roboto-Regular.ttf',
		bold: 'fonts/Roboto-Medium.ttf',
		italics: 'fonts/Roboto-Italic.ttf',
		bolditalics: 'fonts/Roboto-MediumItalic.ttf'
	}
};



var docInfo = {
    initialCorners: null,
    computedItems: null,

    naturalWidth: null,
    naturalHeight: null,

    PDF_FONT_SIZE: null
};



const readFile = file => 
    new Promise((resolve, reject) =>
        fs.readFile(file, (err,data) =>
            err? reject(err) : resolve(data)))


var initialCorners = null

function copyFile(source, target, cb) {
    console.log("\n\n\n\n\n\n COPYING FILE\n\n\n\n\n\n")
    var cbCalled = false;
    
    var rd = fs.createReadStream(source);
    rd.on("error", function(err) {
        done(err);
    });
    var wr = fs.createWriteStream(target);
    wr.on("error", function(err) {
        done(err);
    });
    wr.on("close", function(ex) {
        done();
    });
    rd.pipe(wr);

    var viewBoxDims = 'VB:'



    var spawn = require('child_process').spawn,
    py    = spawn('python', ['python_scripts/mySlant.py', '--filename', 'python_scripts/raw', '--ext', 'jpg']),
    dataString = '';

    py.stdout.on('data', function(data) {
        console.log("Receiving output")
        dataString += data.toString();
    });

    // console.log(viewBoxDims);
    py.stdout.on('end', function() {
        initialCorners = dataString;
        
        console.log("Sending updated values to client")


        myClient.emit('to_client', 'IC:' + initialCorners)
        console.log('IC:' + initialCorners);


        gm("python_scripts/post_skew.png").size(function (err, size) {
            console.log("GM CALLED")
            if (!err) {
                docInfo.naturalWidth = size.width
                docInfo.naturalHeight = size.height
                docInfo.PDF_FONT_SIZE = docInfo.naturalWidth / 60

                viewBoxDims = viewBoxDims + size.width + ',' + size.height
                myClient.emit('to_client', viewBoxDims)
                console.log(viewBoxDims);
            }
        });


    });


    function done(err) {
        if (!cbCalled) {
            cb(err);
            cbCalled = true;
        }
    }
}



var OCR_Step = 0


var myClient = null



const server = http.createServer(async(request, response) => {

    file_name = ""
    file_extension = ""

    console.log(request.method)

    /* THIS WILL EXECUTE ONLY ONCE */
    /* TO UPLOAD THE FILE AND REDIRECT TO client.html */

    if (request.method == 'POST' && OCR_Step==0) {
        // console.log(request.method)
        var form = new formidable.IncomingForm();

        form.parse(request, function (err, fields, files) {
            // console.log("fields.scanupload: ", fields.scanupload)
            if (fields.scanupload == 'true') {

                var oldpath = files.filetoupload.path;

                // var newpath = 'python_scripts/' + files.filetoupload.name;

                filename_arr = files.filetoupload.name.split('.')

                file_name = filename_arr.slice(0, filename_arr.length-1).join('.')
                file_extension = filename_arr[filename_arr.length-1]

                console.log("file_name")
                console.log(file_name)

                console.log("file_extension")
                console.log(file_extension)

                var newpath = "python_scripts/raw." + file_extension

                copyFile(oldpath, newpath, console.log)

                // gm(newpath).size(function (err, size) {
                //     if (!err) {
                //         console.log('width = ' + size.width);
                //         console.log('height = ' + size.height);
                //     }
                // });
            }
        });

        OCR_Step = 1
    }



    console.log(`Request received for "${request.url}"`)
    try {
        webpage = request.url.substr(1).split('?')[0]
        if (webpage=="") {
            webpage = "upload.html"
            OCR_Step = 0
        }

        const data = await readFile(webpage)
        response.end(data)
    } catch (err) {
        response.end()
    }


})

const io = socketio(server)





io.sockets.on('connection', socket => {
    myClient = socket
    myClient.emit('to_client', "WELCOME!")


    // socket.on('to_server', function (data) {
    //     console.log(data);
    // })


    socket.on('step_update', function (data) {
        OCR_Step = data

        console.log(OCR_Step)

        if (OCR_Step==2) {
            /* START LAYOUT ANALYSIS IN PYTHON TOOL */

            var spawn = require('child_process').spawn,
                py    = spawn('python', ['python_scripts/myLayout.py', '--filename', 'python_scripts/post_skew', '--ext', 'png']),
                dataString = '';

            py.stdout.on('data', function(data) {
                receivedData = data.toString()
                console.log(receivedData)
                myClient.emit('to_client', receivedData)
                // dataString += receivedData;
            });

            py.stdout.on('end', function() {
                // console.log(dataString);
                // myClient.emit('to_client', "ITEMS_END")
            });


            /* CLIENT HAS ALREADY RENDERED LAYOUT ANALYSIS SCREEN ON HIS SIDE */


        }

        if (OCR_Step==3) {
            console.log("RUNNING python python_scripts/myCharSplit.py --filename python_scripts/post_skew --ext png --pointsArray")

            /* START CHARACTER SPLIT IN PYTHON TOOL */

            var spawn = require('child_process').spawn,
                py    = spawn('python', ['python_scripts/myCharSplit.py', '--filename', 'python_scripts/post_skew', '--ext', 'png', '--pointsArray', docInfo.computedItems]),
                dataString = '';

            py.stdout.on('data', function(data) {
                receivedData = data.toString()
                // console.log(receivedData)
                // myClient.emit('to_client', receivedData)
                dataString += receivedData;
            });

            py.stdout.on('end', function() {
                console.log("FINAL OUTPUT: ", dataString);
                myClient.emit('to_client', dataString.trim())
            });
        }

        if (OCR_Step==4) {
            console.log("RUNNING python python_scripts/myLeNet.py")


            /* FEED TO NEURAL NETWORK */

            var spawn = require('child_process').spawn,
                py    = spawn('python', ['python_scripts/myLeNet.py']),
                dataString = '';

            py.stdout.on('data', function(data) {
                receivedData = data.toString()
                // console.log(receivedData)
                // myClient.emit('to_client', receivedData)
                dataString += receivedData;
            });

            py.stdout.on('end', function() {
                docInfo.OCRedText = dataString.trim()
                console.log("FINAL OUTPUT: ", docInfo.OCRedText);


                /* WRITE THE PDF FILE!!! */
                /* WRITE THE PDF FILE!!! */
                /* WRITE THE PDF FILE!!! */
                /* WRITE THE PDF FILE!!! */


                doc = new PDFDocument(
                    {
                        size: [docInfo.naturalWidth, docInfo.naturalHeight],
                        margin: 0
                    }
                );
                
                doc.pipe( fs.createWriteStream('python_scripts/ocr_output.pdf') );


                doc.image('python_scripts/post_skew.png', 0, 0)


                doc.fillColor('black', 0.0)
                doc.fontSize(docInfo.PDF_FONT_SIZE)

                itemOnPDF = docInfo.computedItems.substring(1,(docInfo.computedItems).length-1).split('],[')

                IDX_LEFT = 0
                IDX_RIGHT = 1
                IDX_TOP = 2
                IDX_BOTTOM = 3

                console.log("ITERATING OVER THE STRING BY NEWLINE")

                OCRedItem = docInfo.OCRedText.split('\n')

                console.log(OCRedItem)

                itemOnPDF.forEach(function(element, item_idx) {
                    console.log("for writing to PDF")
                    element = element.split(',')
                    console.log(element);

                    doc.text(OCRedItem[item_idx], parseInt(element[IDX_LEFT]), parseInt(element[IDX_TOP]), {width: parseInt(element[IDX_RIGHT]) - parseInt(element[IDX_LEFT])})
                });

                doc.end();

                myClient.emit('to_client', "WROTE_FILE")

            });
        }
    })

    socket.on('step1_correction', function (data) {

        docInfo.initialCorners = data.trim()

        handle_coords = docInfo.initialCorners.split(' ')
        handle_coords = handle_coords.map(x => x.split(','))

        console.log(handle_coords)



        var viewBoxDims = 'VB:'


        
        var spawn = require('child_process').spawn,
        py    = spawn('python', [
            'python_scripts/mySlantCorrector.py', '--filename', 'python_scripts/raw', '--ext', 'jpg',

            '--a1', Math.floor(handle_coords[0][0]).toString(),
            '--a2', Math.floor(handle_coords[0][1]).toString(),
            '--b1', Math.floor(handle_coords[1][0]).toString(),
            '--b2', Math.floor(handle_coords[1][1]).toString(),
            '--c1', Math.floor(handle_coords[2][0]).toString(),
            '--c2', Math.floor(handle_coords[2][1]).toString(),
            '--d1', Math.floor(handle_coords[3][0]).toString(),
            '--d2', Math.floor(handle_coords[3][1]).toString()
        
        ]),
        dataString = '';
    
        py.stdout.on('data', function(data) {
            dataString += data.toString();
        });
    
        py.stdout.on('end', function() {
            initialCorners = dataString;
            
            console.log("Sending updated values to client [post user correction]")
            myClient.emit('to_client', 'IC:' + initialCorners)



            gm("python_scripts/post_skew.png").size(function (err, size) {
                console.log("GM CALLED")
                if (!err) {
                    viewBoxDims = viewBoxDims + size.width + ',' + size.height
                    docInfo.naturalWidth = size.width
                    docInfo.naturalHeight = size.height
                    docInfo.PDF_FONT_SIZE = docInfo.naturalWidth / 60

                    
                    myClient.emit('to_client', viewBoxDims)
                    console.log(viewBoxDims);
                }
            });


            console.log(dataString);
        });



    })


    socket.on('step2_final_items', function (data) {

        docInfo.computedItems = data

        console.log("docInfo.computedItems")
        console.log(docInfo.computedItems)
    })


});












console.log(`Server up and running`)
server.listen(8000)