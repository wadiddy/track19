const COLORS = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#000000'];

function covid_tracker_chart(charts_container, chart_datas, avail_attributes) {
    const verticalLinePlugin = {
        getLinePosition: function (chart, index) {
            const meta = chart.getDatasetMeta(0); // first dataset is used to discover X coordinate of a point
            const data = meta.data;
            return data[index]._model.x;
        },
        renderVerticalLine: function (chartInstance, marker, marker_idx) {
            const lineIndex = chartInstance.scales["x-axis-0"].ticks.indexOf(marker.date);
            const lineLeftOffset = this.getLinePosition(chartInstance, lineIndex);
            let scale_key = null;
            for (s in chartInstance.scales){
                if (s.indexOf("x-axis") != 0){
                    scale_key = s;
                }
            }
            const scale = chartInstance.scales[scale_key];
            const context = chartInstance.chart.ctx;
            const color = "#000000"; COLORS[COLORS.length - (marker_idx + 1)];
            const line_top = scale.top - (-40 + (1 + marker_idx) * 10);

            // render vertical line
            context.beginPath();
            context.strokeStyle = color;
            context.moveTo(lineLeftOffset, line_top);
            context.lineTo(lineLeftOffset, scale.bottom);
            context.stroke();

            // write label
            context.fillStyle = color;
            context.textAlign = 'center';
            context.fillText(marker.text, lineLeftOffset, line_top - 10);
        },

        afterDatasetsDraw: function (chart, easing) {
            if (chart.config.markers) {
                chart.config.markers.forEach(function (marker, idx) {
                    this.renderVerticalLine(chart, marker, idx);
                }.bind(this));
            }
        }
    };
    Chart.plugins.register(verticalLinePlugin);


    const map_attribute_label_value = {}
    avail_attributes.forEach(function (a) {
        map_attribute_label_value[a.value] = a.label;
    });

    const show_tooltips = !$("#id_mobile_checker").is(":visible");

    // Set new default font family and font color to mimic Bootstrap's default styling
    Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
    Chart.defaults.global.defaultFontColor = '#858796';
    Chart.defaults.global.animation.duration = 0;

    Chart.Legend.prototype.afterFit = function() {
        this.height = this.height + 20;
    };

    if (chart_datas.length == 0) {
        $('#chart_configuration_modal').modal('show');
        return
    }

    var labels = []

    chart_datas.forEach(function (chart_data, idx) {
        if (chart_data.series_list.length === 0) {
            return;
        }

        let labels = [];
        for (k in chart_data.series_list[0].data) {
            labels.push(k);
        }

        let y_axis_list = [...new Set(chart_data.series_list.map(function (s) {
            let attr = s.attr;
            let axis_id = attr.indexOf("other_death_") == 0 || attr === "covid_deaths" ? "death" : attr;
            return axis_id;
        }))].map(function (axis_id, idx) {
            let axis_label = axis_id == "death" ? "Deaths per million people" : map_attribute_label_value[axis_id];

            return {
                id: axis_id,
                type: 'linear',
                position: idx === 0 ? 'left' : 'right',
                beginAtZero: true,
                scaleLabel: {
                    fontFamily: 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
                    display: true,
                    labelString: axis_label
                },

                ticks: {
                    min: 0,
                    maxTicksLimit: 5,
                    padding: 10,
                },
                gridLines: {
                    color: "rgb(234, 236, 244)",
                    zeroLineColor: "rgb(234, 236, 244)",
                    drawBorder: false,
                    borderDash: [2],
                    zeroLineBorderDash: [2]
                }
            }
        });

        let datasets = chart_data.series_list.map(function (series_data, idx) {
            var values = []
            for (k in series_data.data) {
                values.push(series_data.data[k]);
            }

            let c = COLORS[idx];

            let axis_id = series_data.attr.indexOf("other_death_") == 0 || series_data.attr == "covid_deaths" ? "death" : series_data.attr;

            return {
                label: series_data.name,
                yAxisID: axis_id,
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                borderColor: c,
                borderWidth: 5,
                pointRadius: 0,
                pointBackgroundColor: c,
                pointBorderColor: c,
                pointHoverRadius: 3,
                pointHoverBackgroundColor: c,
                pointHoverBorderColor: c,
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: values
            }

        });

        let canvas = $("#chart_canvas_" + idx)[0];

        var myLineChart = new Chart(canvas, {
            type: 'line',
            markers: chart_data.markers,
            data: {
                labels: labels,
                datasets: datasets,
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: {
                        left: 10,
                        right: 25,
                        top: 25,
                        bottom: 0
                    }
                },
                scales: {
                    xAxes: [{
                        time: {
                            unit: 'date'
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 7
                        }
                    }],
                    yAxes: y_axis_list,
                },
                legend: {
                    display: true,
                    labels: {
                        fontFamily: 'Nunito,-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif',
                        usePointStyle: true
                    }
                },
                tooltips: {
                    enabled: show_tooltips,
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    intersect: false,
                    mode: 'index',
                    caretPadding: 10,
                    callbacks: {
                        label: function (tooltipItem, chart) {
                            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                            return datasetLabel + ': ' + number_format(tooltipItem.yLabel, 2, ".", true);
                        }
                    }
                }
            }
        });
    });
}

function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function (n, prec) {
            var k = Math.pow(10, prec);
            return '' + Math.round(n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}
