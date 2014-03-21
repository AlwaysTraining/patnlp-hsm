/*
 * This file is provided for custom JavaScript logic that your HTML files might need.
 * Maqetta includes this JavaScript file by default within HTML pages authored in Maqetta.
 */

require(['dojo/store/JsonRest'], function(JsonRest){
	filter_name_store = new JsonRest({
		target: 'filter'
	});
});

require(["dojo/ready"], function(ready){
     ready(function(){
         // logic that requires that Dojo is fully initialized should go here
    	 //load_filter_names();
         dijit.byId('filter_name').store = filter_name_store;
     });
});

function get_methods(obj) {
  var result = [];
  for (var id in obj) {
    try {
      if (typeof(obj[id]) == "function") {
        result.push(id + ": " + obj[id].toString());
      }
    } catch (err) {
      result.push(id + ": inaccessible");
    }
  }
  return result;
}
	
/*
 * Empty settings.
 */
function empty_settings() {
	var settings = new Array()
	settings['filter_name'] = '';
	
	settings['segment_name'] = '';
	settings['segment_value_regex'] = '';
	settings['segment_neg_regex'] = '';
	settings['creates_segment'] = false;
	settings['output_name'] = '';
	
	settings['document_prefix'] = '';
	settings['document_regex'] = '';
	settings['document_neg_regex'] = '';
	
	settings['container_name'] = '';
	settings['container_value_regex'] = '';
	settings['container_neg_regex'] = '';
	settings['container_includes'] = true;
	settings['container_keep_source'] = true;
	
	settings['splitter_left'] = '';
	settings['splitter_regex'] = '';
	settings['splitter_right'] = '';
	settings['splitter_neg_regex'] = '';
	
	settings['mixin_name'] = '';
	settings['mixin_value_regex'] = '';
	settings['mixin_neg_regex'] = '';
	
	return settings;
}

/**
 * Setting names with string values.
 */
function string_settings() {
	var names = ['filter_name',
	             'segment_name', 'segment_value_regex', 'segment_neg_regex', 'output_name',
	             'document_prefix', 'document_regex', 'document_neg_regex',
	             'container_name', 'container_value_regex', 'container_neg_regex',
	             'splitter_left', 'splitter_regex', 'splitter_right', 'splitter_neg_regex',
	             'mixin_name', 'mixin_value_regex', 'mixin_neg_regex']
	return names;
}

/**
 * Settings names with boolean values.
 */
function bool_settings() {
	var names = ['creates_segment', 'container_includes', 'container_keep_source'];
	return names;
}

/*
 * Creates a new filter. Basically just clears the fields.
 */
function new_filter() {
	load_filter(empty_settings());
}

/*
 * Loads filter fields from given settings array.
 */ 
function load_filter(settings) {
	
	var strings = string_settings();
	var bools = bool_settings();
	
	for (var i=0 ; i<strings.length ; ++i) {
		var name = strings[i];
		dijit.byId(name).set('value', settings[name]);
	}
	
	for (var i=0 ; i<bools.length ; ++i) {
		var name = bools[i];
		dijit.byId(name).set('checked', settings[name]);
	}
}

/**
 * Loads ther settings for filter currently selected.
 */
function load_current_filter() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/load",
		content: {'name': name},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else {
				result = result['data'];
				var settings = empty_settings();
				for (var key in result) {
					settings[key] = result[key];
				}
				load_filter(settings);
			}
		}
	});
}

	
/**
 * Collect current settings.
 */
function collect_settings() {
	var settings = new Array();
	var strings = string_settings();
	var bools = bool_settings();
	
	for (var i=0 ; i<strings.length ; ++i) {
		var name = strings[i];
		settings[name] = dijit.byId(name).get('value');
	}
	
	for (var i=0 ; i<bools.length ; ++i) {
		var name = bools[i];
		settings[name] = dijit.byId(name).get('checked');
	}
	return settings;
}

/**
 * Save the filter that is currently edited with the name in the filter name selector.
 */
function save_filter() {
	var settings = collect_settings();
	dojo.xhrPost({
		url: "filter/save_filter",
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

/*
 * Delete the currently selected filter.
 */
function remove_current_filter() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/remove",
		content: {'name': name},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else {
				alert('Removed!');
			}
		}
	});
}
	
/**
 * View a preview of current filter.
 */
function preview_sample() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/preview_sample",
		content: {'name': name},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else {
				result = result['data'];
				dojo.byId('source_html').innerHTML = result['basic'];
				dojo.byId('container_html').innerHTML = result['container'];
				dojo.byId('mixin_html').innerHTML = result['mixin'];
				dojo.byId('splitter_html').innerHTML = result['splitter'];
				dojo.byId('output_html').innerHTML = result['output'];
			}
		}
	});
}

/**
 * Apply current filter to full dataset.
 */
function apply_filter() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/apply_filter",
		content: {'name': name},
		load: function(result) {
			var result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			}
		}
	});
}

/**
 * Update dependency graph of filter nodes.
 */
function update_graph() {
    var width = 500;
    var height = 1000;

    var force = d3.layout.force()
        .linkDistance(256)
        .size([width, height]);
    
    var drag = force.drag().on("dragstart", dragstart);

    dojo.empty('graph_div'); 
    var svg = d3.select('#graph_div').append('svg')
        .attr('width', width)
        .attr('height', height);

    d3.json('filter/graph', function (error, graph) {
        force
            .nodes(graph.nodes)
            .links(graph.links)
            .start();

        var link = svg.selectAll(".link")
            .data(graph.links)
            .enter().append("line")
            .attr("class", "link");

        var node = svg.selectAll(".node")
            .data(graph.nodes)
            .enter().append("g")
            .attr("class", "node")
            .attr('r', 64)
            .call(drag);

        var images = new Array();
        images[1] = 'img/filter_filter.svg';
        images[2] = 'img/filter_input.svg';
        images[3] = 'img/filter_output.svg';

        node.append("image")
            .attr("xlink:href", function(d) { return images[d.group] })
            .attr("x", -32)
            .attr("y", -32)
            .attr("width", 64)
            .attr("height", 64);

        node.append("text")
            .attr("dx", '2em')
            .attr("dy", ".35em")
            .text(function (d) {
                return d.name
            });

        force.on("tick", function () {
            link.attr("x1", function (d) {
                return d.source.x;
            })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                });

            node.attr("transform", function (d) {
                return "translate(" + d.x + "," + d.y + ")";
            });
        });
    });
}

function dblclick(d) {
  d3.select(this).classed("fixed", d.fixed = false);
}

function dragstart(d) {
  d3.select(this).classed("fixed", d.fixed = true);
}

