/*
 * This file is provided for custom JavaScript logic that your HTML files might need.
 * Maqetta includes this JavaScript file by default within HTML pages authored in Maqetta.
 */

require(['dojo/store/JsonRest'], function(JsonRest){
	clusterer_name_store = new JsonRest({
		target: 'clusterer'
	});
	dictionary_store = new JsonRest({
		target: 'dictionary'
	});
});
 
require(["dojo/ready"], function(ready){
     ready(function(){
         // logic that requires that Dojo is fully initialized should go here
    	 dijit.byId('clusterer_name').store = clusterer_name_store;
     });
});

/*
 * Empty settings.
 */
function empty_settings() {
	var settings = new Array()
	settings['clusterer_name'] = '';
	settings['segment_name'] = '';
	settings['dictionary'] = '';
	settings['lda_model'] = '';
	
	return settings;
}

/**
 * Loads ther settings for clusterer currently selected.
 */
function load_current_clusterer() {
	var name = dijit.byId('clusterer_name').get('value');
	dojo.xhrGet({
		url: "clusterer/load",
		content: {'name': name},
		load: function(result) {
			result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else {
				result = result['data'];
				var settings = empty_settings();
				for (var key in result) {
					settings[key] = result[key];
				}
				load_clusterer(settings);
			}
		}
	});
}
	
/** Fill in fields with given clusterer settings */
function load_clusterer(settings) {
	for (var name in settings) {
		dijit.byId(name).set('value', settings[name]);
	}
}

/**
 * Save the clusterer that is currently edited with the name in the filter name selector.
 */
function save_clusterer() {
	var settings = collect_settings();
	dojo.xhrPost({
		url: "clusterer/save",
		content: collect_settings(),
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else if (result['result'] == 'OK') {
				alert('Saved!');
			}
		}
	});
}

/**
 * Collect current settings.
 */
function collect_settings() {
	var settings = empty_settings();
	
	for (var name in settings) {
		settings[name] = dijit.byId(name).get('value');
	}
	return settings;
}

/**
 * Function to update the preview of current clusterer on sample data.
 */
function update_preview() {
	var settings = collect_settings();
	var n = dijit.byId('preview_sample_size').get('value');
	var name = settings['clusterer_name'];

	dojo.xhrPost({
		url: 'clusterer/update',
		content: {'name': name, 'n': n},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else if (result['result'] == 'OK') {

var data = result['data'];
var width = 600;
var height = 500;

var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = width - margin.left - margin.right,
    height = height - margin.top - margin.bottom;

dojo.empty('plot_div'); 
var svg = d3.select('#plot_div').append('svg')
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var xscale = d3.scale.linear()
	.range([0, width]);
var yscale = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
	.scale(xscale)
	.orient("bottom");

var yAxis = d3.svg.axis()
    .scale(yscale)
    .orient("left");

xscale.domain(d3.extent(data, function(p) { return p['x']; })).nice();
yscale.domain(d3.extent(data, function(p) { return p['y']; })).nice();

svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("class", "label")
      .attr("x", width)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("1st component");

svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("2nd component");

svg.selectAll(".dot")
	  .data(data)
	  .enter().append("circle")
	  .attr("class", "dot")
	  .attr("r", 5)
	  .attr("cx", function(p) { return xscale(p['x']); })
	  .attr("cy", function(p) { return yscale(p['y']); })
	  .style("fill", function(p) { return 'red'; })
	  .on("mouseover", function(p) {
		  dojo.html.set(dojo.byId('example_div'), p['document']);
	  })
	  .on("mouseout", function(p) {
		  dojo.html.set(dojo.byId('example_div'), '');
	  });



				alert('Success!');
			}
		}
	});
}
