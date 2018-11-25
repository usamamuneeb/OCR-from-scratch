const socket = io()

var docInfo = {
    initialCorners: null,
    viewBox: null,
    naturalDims: null,

    itemsFound: 0,
    pcntPageAnalysed: 0,

    items: [],
    clientDims: null,

    aspectRatio: 1
};

var step = 1

function detectChange(x) {
    console.log("user changed something")
    console.log(document.getElementById("star-demo").getSVGDocument().getElementById("edit-star").getAttribute("points"))
    socket.emit('step1_correction', document.getElementById("star-demo").getSVGDocument().getElementById("edit-star").getAttribute("points"));
}

function proceedStep(x) {

    if (step==2) {
        /* TO-DO before moving to next stage */

        itemsForOCR = document.getElementsByClassName("resize-drag")

        console.log(itemsForOCR);

        for (var i = 0; i < itemsForOCR.length; i++) {
            itemToOCR = itemsForOCR[i].style

            itemToOCR = [
                parseFloat(itemToOCR.left),
                parseFloat(itemToOCR.left) + parseFloat(itemToOCR.width),
                parseFloat(itemToOCR.top),
                parseFloat(itemToOCR.top) + parseFloat(itemToOCR.height)
            ]

            itemToOCR = itemToOCR.map(function(x) { return x * docInfo.aspectRatio })

            console.log(itemToOCR)
        }
    }

    else {
        ++step
        console.log(step)
        socket.emit('step_update', step);
    }


    redraw()
}


socket.on('to_client', function (data) {
    console.log('server responded:', data);

    if (data.substr(0, 3) == "IC:") {
        docInfo.initialCorners = data.trim().substr(3)

        document.getElementById("star-demo").getSVGDocument().getElementById("edit-star").setAttribute("points", docInfo.initialCorners)
        
        // console.log("UPDATING POINTS to " + docInfo.initialCorners)
        // console.log(document.getElementById("star-demo").getSVGDocument().getElementById("edit-star"))

        handle_coords = docInfo.initialCorners.split(' ')

        for (i = 0; i < handle_coords.length; i++) {
            coords = handle_coords[i].split(',')

            handle = document.getElementById("star-demo").getSVGDocument().querySelector(`[class="point-handle"][data-index="${i}"]`)
            
            handle.setAttribute("x", coords[0])
            handle.setAttribute("y", coords[1])
        }
    }

    else if (data.substr(0, 3) == "VB:") {
        docInfo.viewBox = data.trim().substr(3)
        vb_dims = docInfo.viewBox.split(',')
        console.log(vb_dims)

        docInfo.naturalDims = [parseInt(vb_dims[0]),  parseInt(vb_dims[1])]
        console.log("docInfo.naturalDims")
        console.log(docInfo.naturalDims)

        vb_dims = [Math.round((800 * parseInt(docInfo.naturalDims[0])) / parseInt(docInfo.naturalDims[1])), 800]
        console.log(vb_dims)

        vb_dims = "0 0 " + vb_dims[0].toString() + " " + vb_dims[1].toString()
        console.log(vb_dims)

        document.getElementById("star-demo").getSVGDocument().getElementById("svg-edit-demo").setAttribute("viewBox", vb_dims)
    }

    else if (data.substr(0, 4) == "ITEM") {
        itemInfo = data.trim().split('\r\n')
        
        itemCoords = itemInfo[1]
        itemInfo = itemInfo[0].split('_')

        docInfo.itemsFound = itemInfo[1]
        docInfo.pcntPageAnalysed = itemInfo[3]

        console.log(itemInfo)

        itemCoords = itemCoords.substr(1,itemCoords.length-2).split(', ')
        var itemParams = {
            starting_c: parseInt(itemCoords[0]),
            width: parseInt(itemCoords[1]) - parseInt(itemCoords[0]),
            starting_r: parseInt(itemCoords[2]),
            height: parseInt(itemCoords[3]) - parseInt(itemCoords[2])
        }
        console.log(itemParams)

        docInfo.items.push(itemParams)
        // console.log(docInfo.items)

        /* UPDATE CLIENT DIMS AFTER EVERY ITEM IS RECEIVED (to be in sync with window resizing) */
        docInfo.clientDims = [
            document.getElementById('inner-app-panel').clientWidth,
            document.getElementById('inner-app-panel').clientHeight
        ]

        console.log("CLIENT DIMS: ", docInfo.clientDims)

        docInfo.aspectRatio = docInfo.naturalDims[0] / docInfo.clientDims[0]
    }
    

    redraw();
})



function getStepData(step) {



    if (step==1) {
        return React.createElement('div',{className: "jumbotron"},
        [
            React.createElement('h2', null, "Straightening"),
            React.createElement('p', {className: "lead"}, "If the corners do not look very good, you can adjust them by dragging."),
            
            React.createElement('div',{className: "row"},
            [
                React.createElement('button',{className: "btn btn-success", onClick: ()=>detectChange()}, "Update"),
                React.createElement('button',{className: "btn btn-danger", onClick: ()=>proceedStep()}, "Next")
            ]),
    
            React.createElement('div',{className: "row", style: {marginTop: "20px"}},
            [
                React.createElement('div',{className: "col-lg-6"},
                [
                    React.createElement('object', {id: "star-demo", type: "image/svg+xml", data: "widgets/widget_corners_svg.svg", onMouseUp: (x) => detectChange(x)}, null)
                ]),
                React.createElement('div',{className: "col-lg-6"},
                [
                    React.createElement('img', {src: "python_scripts/post_skew.png?" + new Date().getTime(), style: {width: "100%"}}, null)
                ])
            ]),
        ])
    }




    if (step==2) {

        function getItemOverlays(itemOverlays) {

            console.log("ASPECT RATIO: ", docInfo.aspectRatio)

            itemOverlaysReact = [];

            itemOverlays.forEach(function(overlay) {

                itemOverlaysReact.push(

                    React.createElement('div',{
                        className: "resize-drag",
                        style: {
                            width: (overlay.width / docInfo.aspectRatio).toString() + "px",
                            height: (overlay.height / docInfo.aspectRatio).toString() + "px",
                            left: (overlay.starting_c / docInfo.aspectRatio).toString() + "px",
                            top: (overlay.starting_r / docInfo.aspectRatio).toString() + "px"
                        }
                    }, React.createElement('a', {href: "#"}, 'x'))

                )
            });

            return itemOverlaysReact
        }

        return React.createElement('div',{className: "jumbotron"},
        [
            React.createElement('h2', null, "Layout Analysis"),
            React.createElement('p', {className: "lead"}, `Analysing layout of the page. Please stand by ...`),

            React.createElement('p', {className: "lead"}, `${docInfo.itemsFound} items found, ${docInfo.pcntPageAnalysed}% page analysed.`),
            
            React.createElement('div',{className: "row"},
            [
                // React.createElement('button',{className: "btn btn-success", onClick: ()=>detectChange()}, "Update"),
                React.createElement('button',{className: "btn btn-danger", onClick: ()=>proceedStep()}, "Next")
            ]),
    
            React.createElement('div',{className: "row", style: {marginTop: "20px"}},
            [
                // React.createElement('div',{className: "col-lg-6"},
                // [
                //     React.createElement('img', {src: "python_scripts/post_skew.png?" + new Date().getTime(), style: {width: "100%"}}, null)
                // ]),
                

                React.createElement('div',{className: "col-lg-12", id: "inner-app-panel"},
                [
                    React.createElement('div',{className: "resize-container", style: {
                        background: "green",
                        position: "relative", zIndex: 10
                    }},
                    [
                        React.createElement('img', {
                            src: "python_scripts/post_skew.png?" + new Date().getTime(),
                            style: {width: "100%"},
                        }, null),
                    ]),

                    getItemOverlays(docInfo.items)
                    

                    // React.createElement('div',{
                    //     className: "resize-drag",
                    //     style: {width: "48px", height: "48px", left: "10px", top: "20px"}
                    // }, React.createElement('a', {href: "#"}, 'x'))
                ])

                // React.createElement('div',{className: "col-lg-6"},
                // [
                //     React.createElement('img', {src: "python_scripts/post_layout.png?" + new Date().getTime(), style: {width: "100%"}}, null)
                // ])
            ]),
        ])

        renderWidget_resize();
    }

}

function redraw() {
    ReactDOM.render(
        getStepData(step),
        document.getElementById('ocrFromScratch')
    )

    if (step==1) {
        /* ENLARGE PANEL FOR TWO SIDE BY SIDE PANELS */
        document.getElementById('outer-app-panel').setAttribute("style", "max-width: 1400px")
    }

    if (step==2) {
        /* REDUCE PANEL FOR JUST ONE IMAGE PANEL */
        document.getElementById('outer-app-panel').setAttribute("style", "")

        /* REMOVE PADDING FOR EASIER ALIGNMENT OF LAYOUT ANALYSIS DIV ELEMENTS */
        document.getElementById("inner-app-panel").setAttribute("style", "padding-right: 0px; padding-left: 0px;")



        renderLayoutTool()
    }
}


redraw();