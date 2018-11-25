const socket = io()

var docInfo = {
    initialCorners: null
};

var step = 1

function detectChange(x) {
    console.log("user changed something")
    console.log(document.getElementById("star-demo").getSVGDocument().getElementById("edit-star").getAttribute("points"))
    socket.emit('step1_correction', document.getElementById("star-demo").getSVGDocument().getElementById("edit-star").getAttribute("points"));
}

function proceedStep(x) {
    ++step

    console.log(step)

    socket.emit('step_update', step);

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
        return React.createElement('div',{className: "jumbotron"},
        [
            React.createElement('h2', null, "Layout Analysis"),
            React.createElement('p', {className: "lead"}, `Analysing layout of the page. Please stand by. ${step}`),
            
            React.createElement('div',{className: "row"},
            [
                React.createElement('button',{className: "btn btn-info", onClick: ()=>detectChange()}, "Layout 1"),
                React.createElement('button',{className: "btn btn-info", onClick: ()=>proceedStep()}, "Layout 2")
            ]),
    
            React.createElement('div',{className: "row", style: {marginTop: "20px"}},
            [
                React.createElement('div',{className: "col-lg-6"},
                [
                    React.createElement('img', {src: "python_scripts/post_skew.png?" + new Date().getTime(), style: {width: "100%"}}, null)
                ]),


                React.createElement('div',{className: "col-lg-6"},
                [
                    React.createElement('div',{className: "resize-container"},
                    [
                        React.createElement('div',{className: "resize-drag"}, ".")
                    ])
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

    if (step==2) { renderLayoutTool() }
}


redraw();