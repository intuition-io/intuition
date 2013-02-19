var WIDTH = 800,
	HEIGHT = 500,
	MARGINS = [20, 20, 20, 20],
	visualisation,
	x = d3.scale.linear().range([0 + MARGINS[3], WIDTH - MARGINS[1]]),
	y = d3.scale.linear().range([HEIGHT - MARGINS[0], 0 + MARGINS[2]]),
	r,
	graph,
	plotPoints,
	coasterData,
	newPlot = true,
	cullDirty = false;

visualisation = d3.select("#visualisation");
graph = visualisation.append("svg:g");


function slugify (string) {
	return string.replace (/([^a-z0-9])/ig, '-').toLowerCase ();
}

function generateTypesList (data) {
	var i = data.length,
		typeNames = {},
		select = document.getElementById("coaster-types"),
		list = "";
	while (i--) {
		if (typeof typeNames[data[i].type] == "undefined") {
			typeNames[data[i].type] = data[i].className;
		}
	}
	// TODO: sort out alphabetical list!
	// typeNames.sort();
	//typeNames.forEach (function (option) {
		//list += '<li class="' + typeNames[option] + '"><label><input type="checkbox" checked="checked" value="' + slugify(option) + '">' + option + '</label></li>';
	//});
	for (var key in typeNames) {
		if (typeNames.hasOwnProperty(key)) {
			list += '<li class="' + typeNames[key] + '"><label><input type="checkbox" checked="checked" value="' + slugify(key) + '">' + key + '</label></li>';
		}
	}
	select.innerHTML = list;
}

function generateClassNames (data) {
	var coasterTypes = {},
		counter = 1,
		className;
	data.forEach (function (coaster) {
		className = "";
		if (typeof coasterTypes[coaster.type] == "undefined") {
			coasterTypes[coaster.type] = 'coastertype-' + counter++;
		}
		coaster.className = coasterTypes[coaster.type];
	});
}

// after analysis, dirty data is considered to be that which can't be converted
// to a number, or where the number is 0 (meaning it is unknown)
function cleanup (data) {
	return data.filter (function (coaster) {
		var test = "height opened speed length".split(" ").every (function (attribute) {
			return !isNaN (+coaster[attribute]) && +coaster[attribute] > 0;
		});
		return test;
	});
}

function init (data) {
	if (cullDirty) {
		data = cleanup (data);
	}
	generateClassNames (data);
	generateTypesList (data);

	newPlot = true;
	graph.selectAll ("circle").remove ();

	plotPoints = graph.selectAll ("circle")
		.data(data);

		plotPoints.enter()
			.append ("svg:circle")
			.on("mouseover", function (d) {
				document.getElementById("coastername").innerHTML = d.name;
				d3.select(this).style("stroke-width", 2).style("stroke", "white");
			}).on("mouseout", function (d) {
				document.getElementById("coastername").innerHTML = "";
				d3.select(this).style("stroke-width", 0);
			});

	plotPoints.exit().remove();

	coasterData = data;
	processForm ();
}

function scaleRadius () {
	var max = +document.getElementById("radius-max").value,
		min = +document.getElementById("radius-min").value;

	if (max > 50) max = 50;
	if (max < 0) max = 0;
	if (min < 0) min = 0;
	if (min > 50) min = 50;
	if (isNaN (min)) min = 5;
	if (isNaN (max)) max = 20;

	r = d3.scale.linear().range([min, max]);
}



function plot (xAxis, yAxis, radiusAxis, types) {
	if (typeof radiusAxis === "undefined" || !radiusAxis || radiusAxis === "none") {
		radiusAxis = false;
	}
	scaleRadius ();

	x.domain([
			d3.min(coasterData, function (d) { return +d[xAxis]; }),
			d3.max(coasterData, function (d) { return +d[xAxis]; })
		]);

	y.domain([
			d3.min(coasterData, function (d) { return +d[yAxis]; }),
			d3.max(coasterData, function (d) { return +d[yAxis]; })
		]);

	r.domain([
			d3.min(coasterData, function (d) { return radiusAxis ? +d[radiusAxis] : 5; }),
			d3.max(coasterData, function (d) { return radiusAxis ? +d[radiusAxis] : 5; })
		]);


	if (newPlot) {
		plotPoints.attr("class", function (d) { return d.className; })
			.attr("cx", function (d) { return x (d[xAxis]); })
			.attr("cy", function (d) { return y (d[yAxis]); });
	}

	plotPoints
			.transition().ease("circle-out").duration(1000)
			.attr("r", function (d) {
				if (Array.isArray(types)) {
					if (types.indexOf (slugify(d.type)) !== -1) {
						return radiusAxis ? r (d[radiusAxis]) : 5;
					} else {
						return 0;
					}
				}
				return radiusAxis ? r (d[radiusAxis]) : 5;
			})
			.attr("cx", function (d) { return x (d[xAxis]); })
			.attr("cy", function (d) { return y (d[yAxis]); });

	newPlot = false;
}

function processForm (e) {
	var x = document.querySelector("#x-axis input:checked").value,
		y = document.querySelector("#y-axis input:checked").value,
		r = document.querySelector("#r-axis input:checked").value,
		types = [].map.call (document.querySelectorAll ("#coaster-types input:checked"), function (checkbox) { return checkbox.value;} );


	plot(x, y, r, types);
}

// todo: refactor, change name to selectDdataset. Hard code input id
function onSelectDataset (e) {
	var el = e.target,
		dataset = el.options[el.selectedIndex].value;
	loadDataset (dataset);
}

function onChangeCullDirty (e) {
	cullDirty = !cullDirty;
	onSelectDataset({target:document.getElementById("dataset")});
}

function loadDataset (dataset) {
	d3.csv("data/" + dataset +".csv?" + new Date(), init);
}
onSelectDataset({target:document.getElementById("dataset")});


document.getElementById("cull-dirty").addEventListener ("change", onChangeCullDirty, false);
document.getElementById("dataset").addEventListener ("change", onSelectDataset, false);
document.getElementById("controls").addEventListener ("click", processForm, false);
document.getElementById("controls").addEventListener ("keyup", processForm, false);
