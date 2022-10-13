// SPDX-License-Identifier: MIT
// SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
//
// Interactive map with store locations
//
// TODO: Use webpack or similar to minimize download size.

export function initMap(data) {
    const tilesUrl = `/tiles/${data.brand_id}-brand`
    const map = L.map('map', {zoomControl: false});
    L.control.zoom({position: 'bottomright'}).addTo(map);
    L.tileLayer(  // light_all, light_nolabels, light_only_labels
        'https://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png', {
            minZoom: 1,
            crossOrigin: true,
            attribution:
                '© <a href="http://www.openstreetmap.org/copyright">OSM</a>'
        }).addTo(map);

    const bounds = L.latLngBounds(
        L.latLng(data.bbox[1], data.bbox[0]),
        L.latLng(data.bbox[3], data.bbox[2]));
    map.fitBounds(bounds);
    L.tileLayer(tilesUrl + '/{z}/{x}/{y}.png', {
            attribution: '© ' + data.brand_name,
            bounds: bounds,
            crossOrigin: false
        }).addTo(map);
    map.on('click', function(e) {
		const p = map.project(map.wrapLatLng(e.latlng), map.zoom);
        const tileSize = 256;
        const z = map.getZoom();
		const x = Math.trunc(p.x / tileSize);
		const y = Math.trunc(p.y / tileSize);
		const i = Math.trunc(p.x % tileSize);
		const j = Math.trunc(p.y % tileSize);
		const url = tilesUrl + `/${z}/${x}/${y}/${i}/${j}.geojson`;
		fetch(url, {headers: {'Accept': 'application/geo+json'}})
            .then((response) => response.json())
            .then((data) => console.log(data));
    });

    // TODO:
    //
    // 1. Add a panel to the bottom of the window that later
    //    allows interacting the the content. When the user clicks
    //    on the map, change the panel contents to show the properties
    //    of the clicked feature.
    //
    // 2. Make sure the panel size responds to the screen dimensions.
    //    On a mobile phone held vertically, the panel should be placed
    //    at the bottom of the page; on a desktop screen, the panel
    //    should be at the right of the page. This is can be done
    //    in CSS, see any introduction to responsive web design.
    //
    // 3. When the user moves the mouse, render the overlay tile underneath
    //    the mouse location into a JavaScript canvas, and retrieve the
    //    pixel color at the mouse location. Adjust the mouse cursor shape
    //    depending on whether the pixel is transparent or non-transparent.
    //    This will improve the user experience.
    //
    // As the project matures, this panel will likely be the main
    // user interface for people who work with Brandy. Because it
    // will contain various information and widgets, it really should
    // to be a separate panel on the page, not just a popup bubble
    // on the map.
}
