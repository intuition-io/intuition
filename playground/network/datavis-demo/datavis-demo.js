var WIDTH = 800, // width of the graph
	HEIGHT = 550, // height of the graph
	MARGINS = {top: 20, right: 20, bottom: 20, left: 60}, // margins around the graph
	xRange = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]), // x range function
	yRange = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]), // y range function
	rRange = d3.scale.linear().range([5, 20]), // radius range function - ensures the radius is between 5 and 20
	colours = [	// array of colours for the data points. Each coaster type will have a differnet colour
		"#981C30",
		"#989415",
		"#1E4559",
		"#7F7274",
		"#4C4A12",
		"#ffffff",
		"#4B0612",
		"#1EAAE4",
		"#AD5E71",
		"#000000"
	],
	currentDataset, // name of the current data set. Used to track when the dataset changes
	rawData, // the raw data from the CSV file
	drawingData, // data with the coasters we don't want to display (dirty or it's "type" is unchecked)
	xAxis = d3.svg.axis().scale(xRange).tickSize(16).tickSubdivide(true), // x axis function
	yAxis = d3.svg.axis().scale(yRange).tickSize(10).orient("right").tickSubdivide(true), // y axis function
	vis; // visualisation selection

// runs once when the visualisation loads
function init () {
	vis = d3.select("#visualisation");

	// add in the x axis
	vis.append("svg:g") // container element
		.attr("class", "x axis") // so we can style it with CSS
		.attr("transform", "translate(0," + HEIGHT + ")") // move into position
		.call(xAxis); // add to the visualisation

	// add in the y axis
	vis.append("svg:g") // container element
		.attr("class", "y axis") // so we can style it with CSS
		.call(yAxis); // add to the visualisation

	// load data, process it and draw it
	update ();
}

// this redraws the graph based on the data in the drawingData variable
function redraw () {
	var rollercoasters = vis.selectAll ("circle").data(drawingData, function (d) { return d.id;}), // select the data points and set their data
		axes = getAxes (); // object containing the axes we'd like to use (duration, inversions, etc.)

	// add new points if they're needed
	rollercoasters.enter()
		.insert("svg:circle")
			.attr("cx", function (d) { return xRange (d[axes.xAxis]); })
			.attr("cy", function (d) { return yRange (d[axes.yAxis]); })
			.style("opacity", 0)
			.style("fill", function (d) { return colours[d.type.id]; }); // set fill colour from the colours array

	// the data domains or desired axes might have changed, so update them all
	xRange.domain([
		d3.min(drawingData, function (d) { return +d[axes.xAxis]; }),
		d3.max(drawingData, function (d) { return +d[axes.xAxis]; })
	]);
	yRange.domain([
		d3.min(drawingData, function (d) { return +d[axes.yAxis]; }),
		d3.max(drawingData, function (d) { return +d[axes.yAxis]; })
	]);
	rRange.domain([
		d3.min(drawingData, function (d) { return +d[axes.radiusAxis]; }),
		d3.max(drawingData, function (d) { return +d[axes.radiusAxis]; })
	]);

	// transition function for the axes
    var t = vis.transition().duration(1500).ease("exp-in-out");
    t.select(".x.axis").call(xAxis);
    t.select(".y.axis").call(yAxis);

	// transition the points
	rollercoasters.transition().duration(1500).ease("exp-in-out")
		.style("opacity", 1)
		.style("fill", function (d) { return colours[d.type.id]; }) // set fill colour from the colours array
		.attr("r", function(d) { return rRange (d[axes.radiusAxis]); })
		.attr("cx", function (d) { return xRange (d[axes.xAxis]); })
		.attr("cy", function (d) { return yRange (d[axes.yAxis]); });

	// remove points if we don't need them anymore
	rollercoasters.exit()
		.transition().duration(1500).ease("exp-in-out")
		.attr("cx", function (d) { return xRange (d[axes.xAxis]); })
		.attr("cy", function (d) { return yRange (d[axes.yAxis]); })
			.style("opacity", 0)
			.attr("r", 0)
				.remove();
}

// let's kick it all off!
init ();




//////////////////////////////////////////////////////////
// helper functions - health warning! LOTS of javascript!
//////////////////////////////////////////////////////////

// update the list of checkboxes which allows the selection of coaster types
function generateTypesList (data) {
	var i = data.length,
		typeNames = {},
		select = document.getElementById("coaster-types"),
		list = "";

	// loop though each coaster and check it's type's name. If we haven't seen
	// it before, add it to an object so that we can use it to build the list
	while (i--) {
		if (typeof typeNames[data[i].type.name] == "undefined") {
			typeNames[data[i].type.name] = data[i].type.className;
		}
	}
	// loop through the array to generate the list of types
	for (var key in typeNames) {
		if (typeNames.hasOwnProperty(key)) {
			list += '<li class="' + typeNames[key] + '"><label><input type="checkbox" checked="checked" value="' + slugify(key) + '">' + key + '</label></li>';
		}
	}
	// update the form
	select.innerHTML = list;
}

// return the name of the dataset which is currently selected
function getChosenDataset () {
	var select = document.getElementById("dataset");
	return select.options[select.selectedIndex].value;
}

// take a string and turn it into a WordPress style slug
function slugify (string) {
	return string.replace (/([^a-z0-9])/ig, '-').toLowerCase ();
}

// return an object containing the currently selected axis choices
function getAxes () {
	var x = document.querySelector("#x-axis input:checked").value,
		y = document.querySelector("#y-axis input:checked").value,
		r = document.querySelector("#r-axis input:checked").value;
	return {
		xAxis: x,
		yAxis: y,
		radiusAxis: r
	};
}

// after analysis, dirty data is considered to be that which can't be converted
// to a number, or where the number is 0 (meaning it is unknown)
function isDirty (data) {
	var clean = "duration height opened speed length".split(" ").every (function (attribute) {
		return !isNaN (+data[attribute]) && +data[attribute] > 0;
	});
	return !clean;
}

// return a list of types which are currently selected
function plottableTypes () {
	var types = [].map.call (document.querySelectorAll ("#coaster-types input:checked"), function (checkbox) { return checkbox.value;} );
	return types;
}

// take a raw dataset and remove coasters which shouldn't be displayed
// (i.e. if it is "dirty" or it's type isn't selected)
function processData (data) {
	var processed = [],
		cullDirty = document.getElementById("cull-dirty").checked,
		coasterTypes = {},
		counter = 1;

	data.forEach (function (data, index) {
		var coaster,
			className = "";
		if (!(cullDirty && isDirty(data))) { // don't process it if it's dirty and we want to cull dirty data
				coaster = {
					id: index // so that the coasters can animate
				};
			for (var attribute in data) {
				if (data.hasOwnProperty (attribute)) {
					coaster[attribute] = data[attribute]; // populate the coaster object
				}
			}
			if (typeof coasterTypes[data.type] == "undefined") { // generate a classname for the coaster based on it's type (used for styling)
				coasterTypes[data.type] = {
					id: counter - 1,
					className: 'coastertype-' + counter,
					name: data.type,
					slug: slugify(data.type)
				};
				counter = counter + 1;
			}
			coaster.type = coasterTypes[data.type];
			processed.push (coaster); // add the coaster to the output
		}
	});

	return processed; // only contains coasters we're interested in visualising
}

// remove coasters whose type is not selected from a dataset
function cullUnwantedTypes (coasters) {
	var typesToDisplay = plottableTypes ();

	return coasters.filter (function (coaster) {
		return typesToDisplay.indexOf(coaster.type.slug) !== -1;
	});
}

// called every time a form field has changed
function update () {
	var dataset = getChosenDataset(), // filename of the chosen dataset csv
		processedData; // the data while will be visualised
	// if the dataset has changed from last time, load the new csv file
	if (dataset != currentDataset) {
		d3.csv("data/" + dataset + ".csv", function (data) {
			// process new data and store it in the appropriate variables
			rawData = data;
			processedData = processData(data);
			currentDataset = dataset;
			generateTypesList(processedData);
			drawingData = cullUnwantedTypes(processedData);
			redraw();
		});
	} else {
		// process data based on the form fields and store it in the appropriate variables
		processedData = processData(rawData);
		drawingData = cullUnwantedTypes(processedData);
		redraw();
	}
}

// listen to the form fields changing
document.getElementById("cull-dirty").addEventListener ("change", update, false);
document.getElementById("dataset").addEventListener ("change", update, false);
document.getElementById("controls").addEventListener ("click", update, false);
document.getElementById("controls").addEventListener ("keyup", update, false);
