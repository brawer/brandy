# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Coop Vitality, Swiss pharmacy chain
# https://www.wikidata.org/wiki/Q111725297

import json, re, requests


FEED_URL = 'https://www.coopvitality.ch/de/storepickup/index/loadstore/'


def main():
    features = convert(fetch())
    j = json.dumps(features, sort_keys=True, indent=2, ensure_ascii=False)
    print(j)


def fetch():
    header = {'User-Agent': 'BrandyBot/1.0'}
    return requests.get(FEED_URL, header).json()


def convert(feed):
    stores = [convert_store(s) for s in feed['storesjson']]
    stores.sort(key=lambda s: s['properties']['ref'])
    return {
        'type': 'FeatureCollection',
        'features': stores
    }


def convert_store(s):
    lng, lat = round(float(s['longitude']), 6), round(float(s['latitude']), 6)
    branch = s['store_name'].replace('Coop Vitality', '').strip()
    props = {
        'amenity': 'pharmacy',
        'branch': branch,
        'brand': 'Coop Vitality',
        'brand:wikidata': 'Q111725297',
        'contact:email': s.get('email'),
        'contact:phone': s.get('phone'),
        'healthcare': 'pharmacy',
        'name': 'Coop Vitality',
        'ref': s['galenicare_pharmacy_number']
    }
    props.update(convert_addr(s))
    return {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [lng, lat]},
        'properties': {k: v for k, v in props.items() if v}
    }


def convert_addr(s):
    place, street = s.get('address'), s.get('address_2')
    if not street:
        p = place.split(',', 1)
        place, street = p if len(p) == 2 else (None, p[0])
    m = re.search(r'^\s*(.+?)\s+([0-9]+[A-Za-z]?)$', street)
    housenumber = ''
    if m != None:
        street, housenumber = m.group(1), m.group(2)
    return {
        'addr:city': s.get('city'),
        'addr:country': 'CH',
        'addr:housenumber': housenumber.strip().lower(),
        'addr:place': place,
        'addr:postcode': s.get('zipcode'),
        'addr:street': street
    }


if __name__ == '__main__':
    main()
