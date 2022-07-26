# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import collections, json, os, re, requests, time


FEED_URL = 'https://api.valora-stores.com/_index.php?apiv=2.0.9&a=data&ns=storefinder&l=de&key=%s'


def load(brand):
    with open('keys/com_valora_stores.json') as f:
        api_key = json.load(f)['api_key']
    c = _parse(_fetch(api_key))
    c['features'] = [f for f in c['features']
                     if f['properties'].get('brand:wikidata') == brand]
    return c


Brand = collections.namedtuple('Brand', 'name wikidata tags')

# {'avec box', 'ServiceStoreDB', 'avec X', 'kkiosk', 'k kiosk AUTOMAT', 'Back-Factory', 'Press & Books', 'U-Store', 'Spettacolo', 'Relay', 'Backwerk', 'The Kase', 'Le Crobag', 'Subway', 'avec.', 'Tabacon', 'Hubiz', 'avec express', 'k presse+buch', 'NEWS CAFE', 'Hauptgeschäftsstellen Valora', 'Brezelkönig', 'avec', 'Cigo', 'Naville', 'Ditsch', 'Tabak-Börse', 'Espresso', 'k kiosk'}

_COFFEE_SHOP = {'amenity': 'cafe', 'cuisine': 'coffee_shop'}
_CONVENIENCE = {'shop': 'convenience'}
_PRETZEL = {'amenity': 'fast_food', 'cuisine': 'pretzel'}
_BAKERY = {'shop': 'bakery'}
_KIOSK = {'shop': 'kiosk'}
_NEWSAGENT = {'shop': 'newsagent'}
_BRANDS = {
    'avec': Brand('avec', 'Q103863974', _CONVENIENCE),
    'Back-Factory': Brand('Back-Factory', 'Q21200483', _BAKERY),
    'Backwerk': Brand('BackWerk', 'Q798298', _BAKERY),
    'Brezelkönig': Brand('Brezelkönig', 'Q111728604', _PRETZEL),
    'Cigo': Brand('Cigo', 'Q113290782', _NEWSAGENT),
    'Ditsch': Brand('Ditsch', 'Q911573', _BAKERY),
    'k kiosk': Brand('k kiosk', 'Q60381703', _KIOSK),
    'Press & Books': Brand('Press & Books', 'Q100407277', _NEWSAGENT),
    'ServiceStoreDB': Brand('ServiceStore DB', 'Q84482517', _CONVENIENCE),
    'Spettacolo': Brand('Caffè Spettacolo', 'Q111728781', _COFFEE_SHOP),
    'U-Store': Brand('U-Store', 'Q113290511', _CONVENIENCE),
}
_BRANDS['avec.'] = _BRANDS['avec']
_BRANDS['kkiosk'] = _BRANDS['k kiosk']


def _fetch(api_key):
    os.makedirs('cache', exist_ok=True)
    path, age = os.path.join('cache', 'com_valora_stores.json'), None
    try:
        age = time.time() - os.lstat(path).st_mtime
    except:
        pass
    if not age or age > 86400:  # 1 day in seconds
        with open(path + '.tmp', 'wb') as f:
            t = requests.get(FEED_URL % api_key, {'User-Agent': 'Brandy/1.0'})
            f.write(t.text.encode('utf-8'))
        os.rename(path + '.tmp', path)
    with open(path, 'r') as f:
        return f.read()


def _parse(feed_json):
    feed = json.loads(feed_json)
    brands = _parse_brands(feed)
    countries = _parse_countries(feed)
    stores = feed['items']['stores']
    cols = stores['c']
    features = []
    for store_key, store in stores['r'].items():
        s = _parse_store(store_key, store, cols, brands, countries)
        if s:
            features.append(s)
    features.sort(key=lambda f:f['properties']['ref'])
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def _parse_brands(feed):
    brands = {}
    c = feed['props']['formate']
    cols = c['c']
    for key, val in c['r'].items():
        name = val[cols['format_name']]
        name = name.split('(')[0].strip()
        brand = _BRANDS.get(name)
        if brand:
            brands[int(key)] = brand
    return brands


def _parse_countries(feed):
    countries = {}
    c = feed['props']['laender']
    cols = c['c']
    for key, val in c['r'].items():
        countries[int(key)] = val[cols['land_kuerzel']]
    return countries


def _parse_store(store_key, store, cols, brands, countries):
    brand = brands.get(store[cols['store_format']])
    if not brand:
        return None
    city = store[cols['store_ort']]
    place = store[cols['store_name']].strip()
    if place.startswith(brand.name):
        place = place[len(brand.name):].strip()
    if place.startswith('|'):
        place = place[1:].strip()
    if place == city:
        place = None
    props = {
        'addr:city': city,
        'addr:country': countries[store[cols['store_land']]],
        'addr:housenumber': store[cols['store_strasse_nr']],
        'addr:place': place,
        'addr:postcode': store[cols['store_plz']],
        'addr:street': store[cols['store_strasse']],
        'brand': brand.name,
        'brand:wikidata': brand.wikidata,
        'name': brand.name,
        'ref': store_key,
    }
    props.update(brand.tags)
    props = {k: v for k, v in props.items() if v}
    lng = round(store[cols['store_long']], 7)
    lat = round(store[cols['store_lat']], 7)
    return {
        'type': 'Feature',
        'geometry': {'type': 'Point', 'coordinates': [lng, lat]},
        'properties': props
    }

