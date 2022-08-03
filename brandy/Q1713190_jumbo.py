# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# “Jumbo“ do-it-yourself store, https://www.wikidata.org/wiki/Q1713190

import json, re, requests


FEED_URL = 'https://www.jumbo.ch/yp/de/api/stores'


def _fetch():
    return requests.get(FEED_URL, {'User-Agent': 'Brandy/1.0'}).json()


def _parse(feed):
    stores = [_parse_store(s) for s in feed['stores']]
    stores.sort(key=lambda s: int(s['properties']['ref']))
    return {
        'type': 'FeatureCollection',
        'features': stores
    }


def _parse_store(store):
    lat = round(float(store['location']['latitude']), 6)
    lng = round(float(store['location']['longitude']), 6)
    branch = store['display_name']
    if branch.startswith('JUMBO ') or branch.startswith('Jumbo '):
        branch = branch[6:]
    phone = store.get('phone', '')
    if phone.startswith('0'):
        phone = '+41 ' + phone[1:]
    props = {
        'addr:city': store['city'],
        'addr:country': 'CH',
        'addr:postcode': store['postcode'],
        'branch': branch,
        'brand': 'Jumbo',
        'brand:wikidata': 'Q1713190',
        'contact:email': store.get('email'),
        'contact:phone': phone,
        'name': 'Jumbo',
        'ref': str(store['id']),
        'shop': 'doityourself',
    }
    props.update(_parse_street(store['street']))
    props.update(_parse_opening_hours(store['opening_hours']))
    props.update(_parse_website(store['url']))
    props = {k: v for k, v in props.items() if v}
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "properties": props
    }


def _parse_street(s):
    match = re.match(r'^(.+?)\s+(\d+[A-Za-z]?)$', s)
    if match:
        street, number = match.groups()
        return {'addr:street': street, 'addr:housenumber': number.lower()}
    return {'addr:street': s, 'nohousenumber': 'yes'}


def _parse_opening_hours(hours):
    ranges, last = [], None
    for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']:
        if day in hours:
            from_h = hours[day].get('from', '')[:5]
            to_h = hours[day].get('to', '')[:5]
            if from_h and to_h:
                range_h = '%s-%s' % (from_h, to_h)
                d = day[:2].title()
                if last == range_h:
                    ranges[-1] = ('%s-%s' % (ranges[-1][0][:2], d), range_h)
                else:
                    ranges.append((d, range_h))
                last = range_h
    return {'opening_hours': '; '.join([' '.join(r) for r in ranges])}


def _parse_website(site):
    if site.startswith('/de/filialen/'):
        b = site[13:]
        return {
            'website:de': 'https://www.jumbo.ch/de/filialen/' + b,
            'website:fr': 'https://www.jumbo.ch/fr/filiales/' + b,
            'website:it': 'https://www.jumbo.ch/it/filiali/' + b,
        }
    else:
        return {'website': site}


if __name__ == '__main__':
    features = _parse(_fetch())
    print(json.dumps(features, sort_keys=True, indent=2, ensure_ascii=False))
