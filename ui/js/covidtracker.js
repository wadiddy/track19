function covid_tracker(page_model, avail_locations){

    $(".dropdown-item-attribute").click(function(ev){
        let attribute = $(ev.target).attr("value");
        if ($.inArray(page_model.attributes, attribute) < 0){

            page_model.attributes.push(attribute);
        }
        $("button", $(ev.target).closest(".dropdown")).text($(ev.target).text());

        update_page();
    });

    function update_page(){
        let qs_parts = [];
        qs_parts = qs_parts.concat(page_model.locations.map(function(l){return "loc=" + l;}));
        qs_parts = qs_parts.concat(page_model.attributes.map(function(a){return "attr=" + a;}));

        if (page_model.rolling_average_size){
            qs_parts.push("ravg=" + page_model.rolling_average_size);
        }

        if (page_model.earliest_date){
            qs_parts.push("date_from=" + page_model.earliest_date);
        }

        if (page_model.latest_date){
            qs_parts.push("date_to=" + page_model.latest_date);
        }

        console.log(qs_parts.join("&"));
    }
}