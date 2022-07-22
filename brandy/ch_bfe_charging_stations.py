# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import html, json, os, re, requests, time
import ch_postcodes


FEED_URL = 'https://data.geo.admin.ch/ch.bfe.ladestellen-elektromobilitaet/data/ch.bfe.ladestellen-elektromobilitaet_de.json'



def load(brand):
    c = _convert(_fetch())
    c['features'] = [f for f in c['features']
                     if f['properties'].get('operator:wikidata') == brand]
    return c


def _fetch():
    os.makedirs('cache', exist_ok=True)
    path, age = os.path.join('cache', 'ch_bfe_charging_stations.json'), None
    try:
        age = time.time() - os.lstat(path).st_mtime
    except:
        pass
    if not age or age > 3600 * 3:  # 2 hours in seconds
        with open(path + '.tmp', 'wb') as f:
            t = requests.get(FEED_URL, {'User-Agent': 'Brandy/1.0'})
            f.write(t.text.encode('utf-8'))
        os.rename(path + '.tmp', path)
    with open(path, 'r') as f:
        return f.read()


_BRANDS = {
    'https://www.swisscharge.ch/': ('Q113162249', 'Swisscharge'),
}


def _convert(feed_json):
    feed = json.loads(feed_json)
    features = []
    for f in feed['features']:
        desc = f['properties']['description']
        props = {
            'amenity': 'charging_station',
            'ref': _convert_ref(f['id'])
        }
        props.update(_convert_operator(desc))
        props.update(_convert_addr(desc))
        features.append({
            'type': 'Feature',
            'geometry': f['geometry'],
            'properties': props
        })
    features.sort(key=lambda f:f['properties']['ref'])
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def _convert_operator(desc):
    m = re.search(r'<td class="cell-left">Ladenetzwerk</td>\s+<td><a href="(.+?)"', desc)
    if not m:
        return {}
    url = m.group(1)
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    if url.endswith('.ch') or url.endswith('.eu'):
        url += '/'
    if url not in _BRANDS:
        return {}
    operator_wikidata, operator = _BRANDS[url]
    return {
        'name': operator,
        'operator': operator,
        'operator:wikidata': operator_wikidata
    }


def _convert_addr(desc):
    m = re.search(r'<td class="cell-left">Standort</td>\s*<td>(.+?)</td>', desc)
    if not m:
        return {'addr:country': 'CH'}
    a = html.unescape(m.group(1))
    street, city = a.rsplit(',', 1)
    addr = _convert_city(city)
    addr.update(_convert_street(street))
    return addr


def _convert_city(s):
    s = ' '.join(s.split())
    m = re.search(r'^([-0] )?(\d{4})\s+(.+)$', s)
    if m:
        _, postcode, city = m.groups()
        postcode = int(postcode)
        return {
            'addr:city': city,
            'addr:country': ch_postcodes.country(postcode),
            'addr:postcode': str(postcode)
        }
    city = None
    m = re.search(r'^(0 )?0\s+(.+)$', s)
    if m:
        city = m.group(2).strip()
    elif ch_postcodes.postcodes(s):
        city = s
    if city:
        postcodes = ch_postcodes.postcodes(city)
        if postcodes:
            postcode = min(postcodes)
            return {
                'addr:city': city,
                'addr:country': ch_postcodes.country(postcode),
                'addr:postcode': str(postcode)
            }
        else:
            return {'addr:city': city, 'addr:country': 'CH'}
    return {}


def _convert_street(s):
    s = ' '.join(s.split())
    for pref in ['-']:
        if s.startswith(pref):
            s = s[len(pref):]
    for suff in [' nan', ' -', ' .', '.0', ' 0']:
        if s.endswith(suff):
            s = s[:-len(suff)]
    if s.endswith(' A') or s.endswith(' B'):
        s = s[:-2] + s[-1]
    m = re.search(r'^(.+) ([0-9/\-]+[A-Za-z]?(\.[0-9]+)?)$', s)
    if m:
        street, num, _ = m.groups()
        return {'addr:street': street, 'addr:housenumber': num.lower()}
    words = s.replace('(', ' ').replace(')', ' ').split()
    if '/' in s or ',' in s or any(p in words for p in _placewords):
        return {'addr:place': s, 'nohousenumber': 'yes'}
    return {'addr:street': s, 'nohousenumber': 'yes'}


def _make_placewords():
    p = {'Aire', 'Albergo', 'Autobahn', 'Autoroute', 'Autobahnraststätte',
         'Bahnhof', 'Bushaltestelle', 'Gemeindeparkplatz', 'Feuerwehrlokal',
         'Golfclub', 'Hotel', 'Mehrzweckhalle', 'Museum', 'Parkhaus', 'Parking',
         'Parkplatz', 'Parzelle', 'PP', 'Rastanlage', 'Rastplatz', 'Raststätte',
         'Relais', 'Restauroute', 'SOCAR', 'Tanzplatz', 'Tiefgarage'}
    for word in list(p):
        p.add(word.lower())
    for i in range(1, 30):
        p.add('A%d' % i)
    return p


_placewords = _make_placewords()


def _convert_ref(ref):
    if ref.startswith('CH*SWIEE'):  # Swisscharge
        return str(int(ref[8:]))
    return ref
