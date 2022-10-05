# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import pytest

from brandy.geometry import bbox

def test_bbox():
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

    assert bbox({'type': 'Unsupported geometry type'}) == None
    assert bbox({}) == None
    assert bbox(None) == None
    assert bbox([]) == None
    assert bbox('foo') == None
