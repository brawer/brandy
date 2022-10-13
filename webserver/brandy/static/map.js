// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
//
// Interactive map with store locations
//
// TODO: Use webpack or similar to minimize download size.

export function initMap(data) {
    const map = L.map('map', {zoomControl: false});
    L.control.zoom({position: 'bottomright'}).addTo(map);
    L.tileLayer(  // light_all, light_nolabels, light_only_labels
        'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
            minZoom: 1,
            crossOrigin: true,
            attribution:
                '© <a href="http://www.openstreetmap.org/copyright">OSM</a>'
        }).addTo(map);

    const bbox = data.bbox;
    map.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]]);
    L.tileLayer(
        '/tiles/' + data.brand_id + '-brand/{z}/{x}/{y}.png', {
            crossOrigin: false,
            attribution: '© ' + data.brand_name
        }).addTo(map);

    // TODO:
    //
    // 1. Add a panel to the bottom of the window that later
    //    allows interacting the the content. When the user clicks
    //    on the map, change the panel contents to show the coordinates
    //    of the clicked location.
    //
    // 2. Make sure the panel size responds to the screen dimensions.
    //    On a mobile phone held vertically, the panel should be placed
    //    at the bottom of the page; on a desktop screen, the panel
    //    should be at the right of the page. This is can be done
    //    in CSS, see any introduction to responsive web design.
    //
    // 3. Issue an HTTP request to retrieve the geographic feature
    //    (brand store) at the clicked location. Display its properties
    //    inside the panel.
    //
    // As the project matures, this panel will likely be the main
    // user interface for people who work with Brandy. Because it
    // will contain various information and widgets, it really should
    // to be a separate panel on the page, not just a popup bubble
    // on the map.
}


