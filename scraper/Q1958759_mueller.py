# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Drogerie Müller, European drugstore chain
# https://www.wikidata.org/wiki/Q1958759

import json, re, requests


FEED_DOMAINS = {
    'AT': 'www.mueller.at',
    'CH': 'www.mueller.ch',
    'DE': 'www.mueller.de',
    'ES': 'www.mueller.es',
    'HR': 'www.mueller.hr',
    'HU': 'www.mueller.co.hu',
    'SI': 'www.mueller.si',
}


FEED_URL_PATTERN = 'https://%s/api/ccstore/allPickupStores/'


def main():
    features = convert(fetch())
    j = json.dumps(features, sort_keys=True, indent=2, ensure_ascii=False)
    print(j)


def fetch():
    header = {'User-Agent': 'BrandyBot/1.0'}
    stores = []
    for domain in FEED_DOMAINS.values():
        url = FEED_URL_PATTERN % domain
        stores.extend(requests.get(url, header).json())
    return stores


def convert(feed):
    stores = [convert_store(s) for s in feed]
    stores.sort(key=lambda s: int(s['properties']['ref']))
    return {
        'type': 'FeatureCollection',
        'features': stores
    }


def convert_store(s):
    lng, lat = round(s['longitude'], 6), round(s['latitude'], 6)
    country = s['country'].upper()
    props = {
        'addr:city': s['city'],
        'addr:country': country,
        'addr:postcode': s['zip'],
        'branch': s['storeName'],
        'brand': 'Müller',
        'brand:wikidata': 'Q1958759',
        'name': 'Müller',
        'ref': s['storeNumber'],
        'shop': 'chemist'
    }
    props.update(convert_street(s))
    return {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [lng, lat]},
        'properties': {k: v for k, v in props.items() if v}
    }


def convert_street(s):
    street = s['street'].strip()

    # "Bergheimer Str.4" --> "Bergheimer Str. 4"
    street = re.sub(r'Str\.([0-9])', lambda k:'Str. ' + k.group(1), street)

    # "Augsburger Straße"
    for suffix in [' Straße', ' Str.', 'str.', 'Passage']:
        if street.endswith(suffix):
            return {
                'addr:street': street,
                'nohousenumber': 'yes'
            }

    # "Viktória utca 12 (Szombathely Center)"
    # "Karlsplatz 11-12 (Stachus)"
    m = re.search(r'^(.+)\s+(\d+(?:-\d+)?)\s+\((.+)\)$', street)
    if m != None:
        return {
            'addr:street': m.group(1),
            'addr:housenumber': m.group(2),
            'addr:place': m.group(3)
        }

    # "Karlsplatz 11-13", "Karlsplatz 11 - 13", "Kornmarkt 17/18"
    m = re.search(r'^(.+)\s+(\d+\s*[-/]\s*\d+)$', street)
    if m != None:
        return {
            'addr:street': m.group(1),
            'addr:housenumber': m.group(2).replace(' ', '')
        }

    # "Brunngasse 3+5"
    m = re.search(r'^(.+)\s+(\d+\s*[+]\s*\d+)$', street)
    if m != None:
        return {
            'addr:street': m.group(1),
            'addr:housenumber': m.group(2).replace(' ', '').replace('+', ';')
        }

    # "Karlsplatz 11", "Karlsplatz 11a"
    m = re.search(r'^(.+)\s+(\d+\s*[/]?\s*[A-Za-z]?)$', street)
    if m != None:
        return {
            'addr:street': m.group(1),
            'addr:housenumber': m.group(2).replace(' ', '')
        }

    # "Avinguda Juan Carlos I"
    for prefix in ['Avinguda ']:
        if street.startswith(prefix):
            return {
                'addr:street': street,
                'nohousenumber': 'yes'
            }

    # "City Arkaden"
    return {
        'addr:place': street
    }


if __name__ == '__main__':
    main()