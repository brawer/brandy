# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import pytest
from pytest import approx

from brandy.geometry import bbox, wgs84_to_tile, tile_to_wgs84


def test_wgs84_to_tile():
    assert wgs84_to_tile(8.4, 47.5, 9) == (267, 179)


def test_tile_to_wgs84():
    assert tile_to_wgs84(0, 0, 0) == approx((-180.0, +85.051129))
    assert tile_to_wgs84(0, 1, 1) == approx((+180.0, -85.051129))
    assert tile_to_wgs84(9, 268, 179) == approx((8.437500, 47.517201))


def test_bbox_for_geometry():
    assert bbox({
        'type': 'Point',
        'coordinates': [8, 47]
    }) == (8, 47, 8, 47)

    assert bbox({
         'type': 'LineString',
         'coordinates': [[10, 3], [-2, 2], [11, 1]]
    }) == (-2, 1, 11, 3)

    assert bbox({
        'type': 'Polygon',
        'coordinates': [
            [
                [100.0, 0.0],
                [101.0, 0.0],
                [101.0, 1.0],
                [100.0, -99.9],
                [100.0, 0.0]
            ],
            [
                [100.8, 0.8],
                [100.8, 0.2],
                [123.2, 0.2],
                [100.2, 0.8],
                [100.8, 0.8]
            ]
         ]
     }) == (100.0, -99.9, 123.2, 1.0)

    assert bbox({
         'type': 'MultiPoint',
         'coordinates': [[10, 3], [-2, 2], [11, 1]]
    }) == (-2, 1, 11, 3)

    assert bbox({
        'type': 'MultiLineString',
        'coordinates': [
            [
                [100.0, 0.0],
                [101.0, 1.0]
            ],
            [
                [102.0, 2.0],
                [103.0, 3.0]
            ]
         ]
    }) == (100.0, 0.0, 103.0, 3.0)

    assert bbox({
        'type': 'MultiPolygon',
        'coordinates': [
            [
                [
                    [102.0, 2.0],
                    [103.0, 2.0],
                    [103.0, 3.0],
                    [102.0, 3.0],
                    [102.0, 2.0]
                ]
            ],
            [
                [
                    [100.0, 0.0],
                    [101.0, 0.0],
                    [101.0, 1.0],
                    [100.0, -1.0],
                    [100.0, 0.0]
                ],
                [
                    [100.2, 0.2],
                    [100.2, 0.8],
                    [777.7, 0.8],
                    [100.8, 0.2],
                    [100.2, 0.2]
                ]
            ]
        ]
    }) == (100.0, -1.0, 777.7, 3.0)

    assert bbox({
        'type': 'GeometryCollection',
        'geometries': [{
            'type': 'Point',
            'coordinates': [100.0, 0.0]
        }, {
            'type': 'LineString',
            'coordinates': [
                [101.0, 1.0],
                [102.0, 2.0]
            ]
        }]
    }) == (100.0, 0.0, 102.0, 2.0)

    assert bbox({
        'type': 'GeometryCollection',
        'geometries': []
    }) == None


def test_bbox_for_feature():
    assert bbox({'type': 'Feature'}) == None
    assert bbox({
        'type': 'Feature',
        'geometry': {
            'type': 'Polygon',
            'coordinates': [
               [
                   [-10.0, -10.0],
                   [10.0, -10.0],
                   [10.0, 10.0],
                   [-10.0, -10.0]
               ]
           ]
       }
    }) == (-10.0, -10.0, 10.0, 10.0)


def test_bbox_for_feature_collection():
    assert bbox({
        'type': 'FeatureCollection',
        'features': [{
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [101.0, 0.5]},
            'properties': {'prop0': 'value0'}
        }, {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [
                    [102.0, 0.0],
                    [103.0, 1.0],
                    [104.0, 7.7],
                    [105.0, 1.0]
                ]
            }
        }]
    }) == (101.0, 0.0, 105.0, 7.7)
    assert bbox({'type': 'FeatureCollection'}) == None
    assert bbox({'type': 'FeatureCollection', 'features': []}) == None
    assert bbox({'type': 'FeatureCollection', 'features': None}) == None


def test_bbox_for_junk():
    assert bbox({'type': 'Unsupported type'}) == None
    assert bbox({}) == None
    assert bbox(None) == None
    assert bbox([]) == None
    assert bbox('foo') == None
