# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Geometry-related utility functions

def bbox(o):
    """Compute bounding box of a GeoJSON Feature, FeatureCollection or geometry"""
    if type(o) != dict:
        return None
    t = o.get('type')
    if t == 'Feature':
        return bbox(o.get('geometry'))
    if t == 'FeatureCollection':
        features = o.get('features', [])
        # may be empty as per RFC 7946 section 3.3
        if features == None or len(features) == 0:
            return None
        min_lng, min_lat, max_lng, max_lat = bbox(features[0])
        for f in features[1:]:
            f_min_lng, f_min_lat, f_max_lng, f_max_lat = bbox(f)
            min_lng = min(f_min_lng, min_lng)
            min_lat = min(f_min_lat, min_lat)
            max_lng = max(f_max_lng, max_lng)
            max_lat = max(f_max_lat, max_lat)
        return (min_lng, min_lat, max_lng, max_lat)
    if t == 'GeometryCollection':
        g = o['geometries']
        if len(g) == 0:  # may be empty as per RFC 7946 section 3.1.8
            return None
        min_lng, min_lat, max_lng, max_lat = bbox(g[0])
        for s in g[1:]:
            s_min_lng, s_min_lat, s_max_lng, s_max_lat = bbox(s)
            min_lng = min(s_min_lng, min_lng)
            min_lat = min(s_min_lat, min_lat)
            max_lng = max(s_max_lng, max_lng)
            max_lat = max(s_max_lat, max_lat)
        return (min_lng, min_lat, max_lng, max_lat)
    c = o.get('coordinates')
    if t == 'Point':
        return (c[0], c[1], c[0], c[1])
    if t == 'LineString' or t == 'MultiPoint':
        min_lng = max_lng = c[0][0]
        min_lat = max_lat = c[0][1]
        for p in c[1:]:
            lng, lat = p[0], p[1]
            min_lng, min_lat = min(lng, min_lng), min(lat, min_lat)
            max_lng, max_lat = max(lng, max_lng), max(lat, max_lat)
        return (min_lng, min_lat, max_lng, max_lat)
    if t == 'Polygon' or t == 'MultiLineString':
        min_lng = max_lng = c[0][0][0]
        min_lat = max_lat = c[0][0][1]
        for r in c:
            for p in r:
                lng, lat = p[0], p[1]
                min_lng, min_lat = min(lng, min_lng), min(lat, min_lat)
                max_lng, max_lat = max(lng, max_lng), max(lat, max_lat)
        return (min_lng, min_lat, max_lng, max_lat)
    if t == 'MultiPolygon':
        min_lng = max_lng = c[0][0][0][0]
        min_lat = max_lat = c[0][0][0][1]
        for multipoly in c:
            for ring in multipoly:
                for p in ring:
                    lng, lat = p[0], p[1]
                    min_lng, min_lat = min(lng, min_lng), min(lat, min_lat)
                    max_lng, max_lat = max(lng, max_lng), max(lat, max_lat)
        return (min_lng, min_lat, max_lng, max_lat)
    return None
