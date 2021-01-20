import * as d3 from "d3";
import * as cmk_figures from "cmk_figures";
import * as utils from "utils";

// Used for rapid protoyping, bypassing webpack
// var cmk_figures = cmk.figures; /* eslint-disable-line no-undef */
// var dc = dc; /* eslint-disable-line no-undef */
// var d3 = d3; /* eslint-disable-line no-undef */
// var crossfilter = crossfilter; /* eslint-disable-line no-undef */

class SiteOverview extends cmk_figures.FigureBase {
    static ident() {
        return "site_overview";
    }

    constructor(div_selector, fixed_size = null) {
        super(div_selector, fixed_size);
        this.margin = {top: 0, right: 0, bottom: 0, left: 0};
    }

    initialize(debug) {
        cmk_figures.FigureBase.prototype.initialize.call(this, debug);
        this.svg = this._div_selection.append("svg");
        this.plot = this.svg.append("g");
    }

    update_data(data) {
        // Data format (based on cmk_figures general data format)
        // {"data" :
        //   [
        //    {
        //      "name": "munich",
        //      "values"
        //      "count_warning": 22,
        //      "count_critical": 22,
        //      "count_in_downtime": 22,
        //    }
        //   ],
        //  "plot_definitions" : [
        //    {
        //       "display_optionA": blabla
        //    }
        //   ]
        // }
        cmk_figures.FigureBase.prototype.update_data.call(this, data);
        this._crossfilter.remove(() => true);
        this._crossfilter.add(this._data.data);
    }

    resize() {
        cmk_figures.FigureBase.prototype.resize.call(this);
        this.svg.attr("width", this.figure_size.width);
        this.svg.attr("height", this.figure_size.height);
    }

    update_gui() {
        this.resize();

        if (this._data.render_mode == "hosts") {
            this.render_hosts();
        } else if (this._data.render_mode == "sites") {
            this.render_sites();
        }

        this.render_title(this._data.title);
    }

    render_hosts() {}

    render_sites() {
        let width = this.plot_size.width;
        let height = this.plot_size.height;

        // TODO: The dashlet can be configured to NOT show a title. In this case the render()
        // method must not apply the header top margin (24px, see FigureBase.render_title)
        let header_height = 24;
        // Effective height of the label (based on styling)
        let label_height = 11;
        let label_v_padding = 8;
        let min_label_width = 60;

        // Spacing between dashlet border and box area
        let canvas_v_padding = 10;
        let canvas_h_padding = 4;
        // The area where boxes are rendered to
        let box_area_top = header_height + canvas_v_padding;
        let box_area_left = canvas_h_padding;
        let box_area_width = width - 2 * canvas_h_padding;
        let box_area_height = height - box_area_top - canvas_v_padding;

        // Must not be larger than the "host/service statistics" hexagons
        let max_box_width = 114;
        let box_v_rel_padding = 0.05;
        let box_h_rel_padding = 0;
        // Calculating the distance from center to top of hexagon
        let hexagon_max_radius = max_box_width / 2;

        let num_elements = this._data.data.length;

        if (box_area_width < 20 || box_area_height < 20) {
            return; // Does not make sense to continue
        }

        // Calculate number of columns and rows we need to render all elements
        let num_columns = Math.max(Math.floor(box_area_width / max_box_width), 1);

        // Rough idea of this algorithm: Increase the number of columns, then calculate the number
        // of rows needed to fit all elements into the box_area. Then calculate the box size based
        // on the number of columns and available space. Then check whether or not it fits into the
        // box_are.  In case it does not fit, increase the number of columns (which then may also
        // decrease the size of the box sizes).
        let compute_geometry = function (num_columns) {
            let num_rows = Math.ceil(num_elements / num_columns);
            // Calculating the distance from center to top of hexagon
            let box_width = box_area_width / num_columns;

            let hexagon_radius = Math.min(box_width / 2, hexagon_max_radius);
            hexagon_radius -= hexagon_radius * box_h_rel_padding;

            let necessary_box_height = hexagon_radius * 2 * (1 + box_v_rel_padding);

            let show_label = box_width >= min_label_width;
            if (show_label) necessary_box_height += label_v_padding * 2 + label_height;

            if (num_columns == 100) {
                return null;
            }

            if (necessary_box_height * num_rows > box_area_height) {
                // With the current number of columns we are not able to render all boxes on the
                // box_area. Next, try with one more column.
                return null;
            }

            let box_height = box_area_height / num_rows;
            let hexagon_center_top =
                hexagon_radius * (1 + box_v_rel_padding) + (box_height - necessary_box_height) / 2;

            let label_baseline_top =
                hexagon_center_top + hexagon_radius + label_height + label_v_padding;

            // Reduce number of columns, trying to balance the rows
            num_columns = Math.ceil(num_elements / num_rows);
            box_width = box_area_width / num_columns;

            let hexagon_center_left = box_width / 2;
            let label_center_left = box_width / 2;

            return {
                num_columns: num_columns,
                hexagon_center_top: hexagon_center_top,
                hexagon_center_left: hexagon_center_left,
                hexagon_radius: hexagon_radius,
                box_width: box_width,
                box_height: box_height,
                show_label: show_label,
                label_baseline_top: label_baseline_top,
                label_center_left: label_center_left,
            };
        };

        let geometry = null;
        while (geometry === null) {
            geometry = compute_geometry(num_columns++);
        }

        let boxes = this.svg
            .selectAll("g.main_box")
            .data(this._data.data)
            .join(enter => enter.append("g").classed("main_box", true));

        let hexagon_center_pos =
            "translate(" + geometry.hexagon_center_left + "," + geometry.hexagon_center_top + ")";

        let handle_click = function (d) {
            location.href = utils.makeuri({site: d.site_id});
        };

        let handle_mouseover = function () {
            d3.select(this).style("opacity", 0.8);
        };

        let handle_mouseout = function () {
            d3.select(this).style("opacity", 1);
        };

        let boxes_centered_g = boxes
            .selectAll("g")
            .data(d => [d])
            .join("g")
            .attr("transform", hexagon_center_pos)
            .style("cursor", "pointer")
            .on("click", handle_click)
            .on("mouseover", handle_mouseover)
            .on("mouseout", handle_mouseout);

        boxes_centered_g
            .selectAll("path.outer_line")
            .data(d => [d])
            .join(enter => enter.append("path").classed("outer_line", true))
            .attr("d", d3.hexbin().hexagon(geometry.hexagon_radius))
            .attr("stroke", "#13d389");

        boxes_centered_g
            .selectAll("path.inner_line")
            .data(d => [d])
            .join(enter => enter.append("path").classed("inner_line", true))
            .attr("d", d3.hexbin().hexagon(geometry.hexagon_radius / 2))
            .attr("fill", "yellow");

        if (geometry.show_label) {
            boxes
                .selectAll("text")
                .data(d => [d.title])
                .join("text")
                .text(d => d)
                .attr("x", function () {
                    return geometry.label_center_left - this.getBBox().width / 2;
                })
                .attr("y", function () {
                    return geometry.label_baseline_top;
                })
                .style("cursor", "pointer")
                .on("click", handle_click)
                .on("mouseover", handle_mouseover)
                .on("mouseout", handle_mouseout);
        } else {
            boxes.selectAll("text").remove();
        }

        // Place boxes
        boxes.transition().attr("transform", (d, idx) => {
            let x = (idx % geometry.num_columns) * geometry.box_width;
            let y = Math.trunc(idx / geometry.num_columns) * geometry.box_height;
            return "translate(" + (x + box_area_left) + "," + (y + box_area_top) + ")";
        });
    }
}

cmk_figures.figure_registry.register(SiteOverview);
