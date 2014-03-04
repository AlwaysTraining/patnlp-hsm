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
	var method = dijit.byId('dimensionality_reduction').get('value');

	dojo.xhrPost({
		url: 'clusterer/update',
		content: {'name': name, 'n': n, 'method': method},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else if (result['result'] == 'OK') {
				var data = result['data'];
				plot_data = data
				update_svg_preview(data);
				alert('Updated!');
			}
		}
	});
}

// global variable for plot data
plot_data = new Array();

function update_svg_preview(data) {
	plot_data = data;
	
	var width = 800;
	var height = 600;

	var margin = {top: 20, right: 20, bottom: 30, left: 40},
	    width = width - margin.left - margin.right,
	    height = height - margin.top - margin.bottom;

	dojo.empty('plot_div'); 
	var svg = d3.select('#plot_div').append('svg')
	    .attr("id", 'plot_svg')
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
	
	var color = d3.scale.category10();

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
		  .attr("label", function(p) { return p['label']; })
		  .style("fill", function(p) { return color(p['label']); })
		  .on("click", function(p) {
			  var label = prompt("Enter label for " + p['document'], p['label']);
			  if (label != null) { // if user did not press cancel
				  plot_data[p['idx']]['label'] = label;
				  update_svg_preview(plot_data);
			  }  
          })
		  .on("mouseover", function(p) {
			  dojo.html.set(dojo.byId('example_div'), p['document']);
		  })
		  .on("mouseout", function(p) {
			  dojo.html.set(dojo.byId('example_div'), '');var svg = d3.select('#plot_div')
		  });
	
	var legend = svg.selectAll(".legend")
	  .data(color.domain())
	.enter().append("g")
	  .attr("class", "legend")
	  .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });
	
	  legend.append("rect")
	  .attr("x", width - 18)
	  .attr("width", 18)
	  .attr("height", 18)
	  .style("fill", color);
	
	  legend.append("text")
	  .attr("x", width - 24)
	  .attr("y", 9)
	  .attr("dy", ".35em")
	  .style("text-anchor", "end")
	  .text(function(p) { return p; });
}

function clear_labels() {
	var settings = collect_settings();
	var name = settings['clusterer_name'];
	if (confirm('Do you really want to clear ALL labels?')) {
		dojo.xhrPost({
			url: 'clusterer/clear_labels',
			content: {'name': name},
			load: function(result) {
				var result = JSON.parse(result);
				if (result['result'] === 'FAIL') {
					alert(result['error']);
				} else if (result['result'] == 'OK') {
					alert('Cleared!');
				}
			}
		});
	}
}

function save_labels() {
	var settings = collect_settings();
	var name = settings['clusterer_name'];
	var content = {'name': name, 'labels': JSON.stringify(get_labels_dict(plot_data))};

	dojo.xhrPost({
		url: 'clusterer/save_labels',
		content: content,
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

function get_labels_dict(data) {
	var result = {};
	for (var idx in data) {
		var point = data[idx];
		if (point['label'] != 'unknown') {
			result[point['document']] = point['label'];
		}
	}
	return result;
}


function propagate_labels() {
	
}

function show_unknown() {
	var svg = d3.select('#plot_svg');
	var circle = svg.selectAll('circle');
	circle.style("display", 'block');
}

function hide_unknown() {
	var svg = d3.select('#plot_svg');
	var circle = svg.selectAll('circle');
	circle.style("display", hider);
}

/**
 * Helper functio to hide 'unknown' datapoints.
 */
function hider(datapoint) {
	if (datapoint['label'] == 'unknown') {
		return 'none';
	}
	return 'block';
}

function view_examples() {
	var settings = collect_settings();
	var n = dijit.byId('preview_sample_size').get('value');
	var name = settings['clusterer_name'];
	var load = window.open('/clusterer/view_examples?name=' + name + '&n=' + n, "examples", "scrollbars=1,location=1,status=1");
}
