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
                '© <a href="http://www.openstreetmap.org/copyright">OSM</a>' +
              ' · ' + data.brand_name
    }).addTo(map);;

    const bbox = data.bbox;
    map.fitBounds([[bbox[1], bbox[0]], [bbox[3], bbox[2]]]);
    L.polygon([
        [bbox[1], bbox[0]],
        [bbox[1], bbox[2]],
        [bbox[3], bbox[2]],
        [bbox[3], bbox[0]]
    ]).addTo(map).bindPopup('TODO: Show markers');

    fetch(data.items_url, {headers: {Accept: 'application/geo+json'}})
        .then(response => response.json())
        .then(features => console.log(features));
}


