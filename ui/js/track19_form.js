function covid_tracker_form(page_model, avail_locations, avail_attributes) {
    const map_location_token_name = {}
    avail_locations.forEach(function (l) {
        map_location_token_name[l.token] = l.name;
    });

    const map_attribute_label_value = {}
    avail_attributes.forEach(function (a) {
        map_attribute_label_value[a.value] = a.label;
    });

    $(".btn_copy_chart").click(function(ev){
        let chart_index = $(ev.target).closest(".chart_card").data("chart_index");
        let chart_to_copy = page_model.charts[chart_index];
        page_model.charts.splice(chart_index, 0, {
            "name": chart_to_copy.name,
            "locations": chart_to_copy.locations.map(function(l){return l;}),
            "attributes": chart_to_copy.attributes.map(function(a){return a;}),
        });
        update_page();
        return false;
    });

    $(".btn_remove_chart").click(function(ev){
        let chart_index = $(ev.target).closest(".chart_card").data("chart_index");
        page_model.charts.splice(chart_index, 1);
        update_page();
        return false;
    });

    $('#global_configuration_modal')
        .on('click', '.btn-primary', function(ev){
            page_model.rolling_average_size = $('#global_configuration_modal #inp_rolling_average_size').val();
            page_model.earliest_date = $('#global_configuration_modal #inp_earliest_date').val();
            page_model.latest_date = $('#global_configuration_modal #inp_latest_date').val();
            update_page();
            return false;
        })
    ;

    $('#chart_configuration_modal')
        .on('show.bs.modal', function (ev) {
            let button = $(ev.relatedTarget);
            if (isNaN(button.data('chart_index'))) {
                $("#chart_configuration_modal .modal-title").text("Add a new Chart");
            } else {
                $("#chart_configuration_modal .modal-title").text("Edit Chart");
            }

            let chart_data = page_model.charts[button.data('chart_index')];
            if (!chart_data) {
                chart_data = {
                    "name": null,
                    "locations": [],
                    "attributes": [],
                }
                page_model.charts.unshift(chart_data);
            }

            $('#chart_configuration_modal').data("chart_data", chart_data);
            paint_modal_with_chart_data();
        })
        .on('click', '.btn-primary', function(ev){
            update_page();
            return false;
        })
        .on('click', '.a_remove_attribute', function (ev) {
            let attribute_token = $(ev.target).closest("li").data('attribute_token');
            let chart_data = $('#chart_configuration_modal').data("chart_data");
            chart_data.attributes = chart_data.attributes.filter(function (at) {
                return at !== attribute_token;
            });
            paint_modal_with_chart_data();
            return false;
        })
        .on('click', '.a_remove_location', function (ev) {
            let location_token = $(ev.target).closest("li").data('location_token');
            let chart_data = $('#chart_configuration_modal').data("chart_data");
            chart_data.locations = chart_data.locations.filter(function (lt) {
                return lt !== location_token;
            });
            paint_modal_with_chart_data();
            return false;
        });

    $("#btn_add_metric").on("click", ".dropdown-item", function (ev) {
        let chart_data = $('#chart_configuration_modal').data("chart_data");
        chart_data.attributes.push($(ev.target).attr("value"));
        $("#btn_add_metric").dropdown("toggle");
        paint_modal_with_chart_data();

        return false;
    });


    $(".location-selector")
        .typeahead({
                hint: true,
                highlight: true,
                minLength: 1
            },
            {
                name: 'locations',
                source: function (query, process) {
                    map_location_label_id = {}
                    options = []
                    avail_locations.forEach(function (l) {
                        map_location_label_id[l.name] = l.token
                        options.push(l.name)
                    });
                    process(findMatches(options, query))
                }
            })
        .bind('typeahead:select', function (ev, suggestion) {
            let chart_data = $(ev.target).closest(".modal").data("chart_data");
            chart_data.locations.push(map_location_label_id[suggestion]);
            $('.location-selector').typeahead('val', '');

            paint_modal_with_chart_data();
        })
    ;

    function paint_modal_with_chart_data() {
        let chart_data = $('#chart_configuration_modal').data("chart_data");

        let locations_container = $("#chart_configuration_modal .div_modal_locations_container");
        locations_container.empty();
        [...new Set(chart_data.locations)].sort().forEach(function (location_token) {
            let location_name = map_location_token_name[location_token]

            locations_container.append("<li data-location_token='" + location_token + "' class='small text-gray-700'>" + location_name + "&nbsp;(<a class='a_remove_location' title='Remove Location' href='#'>x</a>)</li>");
        });

        let attributes_contianer = $("#chart_configuration_modal .div_modal_attributes_container");
        attributes_contianer.empty();
        chart_data.attributes.forEach(function (attribute_token) {
            let attribute_name = map_attribute_label_value[attribute_token]
            attributes_contianer.append("<li data-attribute_token='" + attribute_token + "' class='small text-gray-700'>" + attribute_name + "&nbsp;(<a class='a_remove_attribute' title='Remove Metric' href='#'>x</a>)</li>");
        });

    }

    function update_page() {
        let qs_parts = [];

        if (page_model.rolling_average_size) {
            qs_parts.push("ravg=" + page_model.rolling_average_size);
        }

        if (page_model.earliest_date) {
            qs_parts.push("date_from=" + page_model.earliest_date);
        }

        if (page_model.latest_date) {
            qs_parts.push("date_to=" + page_model.latest_date);
        }

        page_model.charts.forEach(function(chart_data, idx){
            let suffix = idx === 0 ? "" : "" + idx;

            if (chart_data.name){
                qs_parts.push("name" + suffix + "=" + chart_data.name);
            }
            chart_data.locations.forEach(function(l){
                qs_parts.push("loc" + suffix + "=" + l);
            });
            chart_data.attributes.forEach(function(a){
                qs_parts.push("attr" + suffix + "=" + a);
            });
        });

        window.location = "/?" + qs_parts.join("&");
    }
}

function findMatches(strs, q) {
    var matches, substringRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function (i, str) {
        if (substrRegex.test(str)) {
            matches.push(str);
        }
    });

    return matches;
}
