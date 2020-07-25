function covid_tracker_form(page_model, avail_locations) {
    $(".dropdown-item-attribute").click(function (ev) {
        $("button", $(ev.target).closest(".dropdown")).text($(ev.target).text());

        let attribute = $(ev.target).attr("value");
        page_model.attributes = [attribute];
        // if ($.inArray(page_model.attributes, attribute) < 0) {
        //     page_model.attributes.push(attribute);
        // }

        update_page();
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
            let location_token = map_location_label_id[suggestion];
            page_model.locations = [location_token];
            // if ($.inArray(page_model.locations, location_token) < 0) {
            //     page_model.locations.push(location_token);
            // }
            update_page();
        })
    ;

    function update_page() {
        let qs_parts = [];
        qs_parts = qs_parts.concat(page_model.locations.map(function (l) {
            return "loc=" + l;
        }));
        qs_parts = qs_parts.concat(page_model.attributes.map(function (a) {
            return "attr=" + a;
        }));

        if (page_model.rolling_average_size) {
            qs_parts.push("ravg=" + page_model.rolling_average_size);
        }

        if (page_model.earliest_date) {
            qs_parts.push("date_from=" + page_model.earliest_date);
        }

        if (page_model.latest_date) {
            qs_parts.push("date_to=" + page_model.latest_date);
        }

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
