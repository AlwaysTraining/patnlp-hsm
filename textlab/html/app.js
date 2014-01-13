/*
 * This file is provided for custom JavaScript logic that your HTML files might need.
 * Maqetta includes this JavaScript file by default within HTML pages authored in Maqetta.
 */
require(["dojo/ready"], function(ready){
     ready(function(){
         // logic that requires that Dojo is fully initialized should go here
    	 load_filter_names();
     });
});

/*
 * Load filter names into filter name selector.
 */
function load_filter_names() {
	dojo.xhrGet({
		url: "filter/available_filters",
		load: function(result) {
			//var store = new dojo.data.ItemFileReadStore({data: {identifier: 'filter_name', label: 'filter_name', items: result}});
			//alert (store);
			//dijit.byId('filter_name').store = store;
		}
	});
}

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
			result = JSON.parse(result);
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
			result = JSON.parse(result)
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else if (result['result'] == 'OK') {
				alert('Saved!');
			}
		}
	});
}

function preview_sample() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/preview_sample",
		content: {'name': name},
		load: function(result) {
			result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			} else {
				result = result['data'];
				dojo.byId('source_html').innerHTML = result['source'];
				dojo.byId('output_html').innerHTML = result['output'];
			}
		}
	});
}

function apply_filter() {
	var name = dijit.byId('filter_name').get('value');
	dojo.xhrGet({
		url: "filter/apply_filter",
		content: {'name': name},
		load: function(result) {
			result = JSON.parse(result);
			if (result['result'] === 'FAIL') {
				alert(result['error']);
			}
		}
	});
}
