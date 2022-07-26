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


# Counter({'https://www.ecarup.com/': 1480, 'https://www.evpass.ch/': 1194, 'https://www.move.ch/': 724, 'https://www.swisscharge.ch/': 716, 'https://plugnroll.com': 142, 'https://www.lidl.ch/de/unternehmen/filialen-oeffnungszeiten/e-tankstellen': 39, 'https://www.eniwa.ch/': 30, 'https://www.tesla.com/de_CH/supercharger': 22, 'https://www.mobilecharge.ch/': 17, 'https://deviwa.ch/': 14, 'https://www.migrol.ch/de/mobilit%C3%A4t/fast-charging/': 14, 'https://payment.ionity.eu/': 10, 'https://www.ewd.ch/e-tankstellen-in-davos': 8, 'https://www.ewo.ch/privatkunden/elektromobilitaet/': 7, 'https://www.energieuri.ch/privatkunden/elektromobilitaet-photovoltaik-eigenverbrauch/elektromobilitaet': 7, 'https://ebs.swiss/elektromobilitaet/': 6, 'https://www.parkandcharge.ch/': 3, 'https://www.ckw.ch/mobimo': 3, 'https://www.evaltendorf.ch/e-mobilitaet': 2, 'https://fastnedcharging.com/de/': 2, 'https://www.chocolatfrey.ch/': 1, 'https://www.herrliberg.ch/verwaltung/dienstleistungen-a-z.html/217/egov_service/443': 1, 'https://www.villa.ch/': 1, 'https://www.dietikon.ch/wohnenarbeiten/wohnen/mobilitaet/parkieren/4035': 1, 'https://osterwalder.ch/': 1, 'https://paccom.ch/willkommen/': 1, 'https://www.ail.ch/': 1})


_OPERATORS = {
    'https://www.ecarup.com/': ('Q113192759', 'eCarUp'),
    'https://www.evpass.ch/': ('Q113270804', 'evpass'),
    'https://www.move.ch/': ('Q110278557', 'MOVE'),
    'https://www.swisscharge.ch/': ('Q113162249', 'Swisscharge'),
    'https://www.tesla.com/de_CH/supercharger': ('Q17089620', 'Tesla Supercharger'),
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
        props.update(_convert_access(desc))
        props.update(_convert_addr(desc))
        props.update(_convert_socket(desc))
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


def _convert_access(desc):
    m = re.search(r'<td class=\"[^"]*\">Zugang</td>\s+<td>(.+?)</', desc)
    if not m:
        return {}
    # As of July 2022, the upstream feed contains contradicting access info
    # such as "Eingeschränkt zugänglich, Öffentlich zugänglich".
    # We want to return the most restrictive of such tags, so the order
    # of tests matter here (should be from most to least restrictive).
    s = {s.strip() for s in m.group(1).split(',')}
    if 'Keine Angabe' in s:
        return {'access': 'unknown'}
    if 'Eingeschränkt zugänglich' in s:
        return {'access': 'limited'}
    if 'Öffentlich zugänglich' in s:
        return {'access': 'permissive'}
    return {}


def _convert_operator(desc):
    m = re.search(r'<td class="cell-left">Ladenetzwerk</td>\s+<td><a href="(.+?)"', desc)
    if not m:
        return {}
    url = m.group(1)
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    if url.endswith('.ch') or url.endswith('.eu') or url.endswith('.com'):
        url += '/'
    if url not in _OPERATORS:
        return {}
    operator_wikidata, operator = _OPERATORS[url]
    return {
        'name': operator,
        'operator': operator,
        'operator:wikidata': operator_wikidata
    }


# https://wiki.openstreetmap.org/wiki/Key:socket
_SOCKETS = {
    'CCS': ('type2_combo', None),
    'CHAdeMO': ('chademo', None),
    'Haushaltsteckdose CH': ('sev1011_t13', 230),
    'Haushaltsteckdose Schuko': ('schuko', 230),
    'IEC 60309': ('cee_blue', 230),
    'Kabel Typ 1': ('type1_cable', None),
    'Kabel Typ 2': ('type2_cable', None),
    'Steckdose Typ 2': ('type2', None),
    'Steckdose Typ 3': ('type3', None),
    'Tesla': ('tesla_supercharger', None),
}


def _convert_socket(desc):
    num_sockets, max_output, max_voltage = {}, {}, {}
    for table in desc.split('<table class="evse-overview')[1:]:
        for tr in table.split('</table>')[0].split('</tr>')[1:]:
            m = re.search(r'<td>\s*(.+?)\s*<', tr)
            if not m:
                continue
            socket, voltage = _SOCKETS.get(m.group(1), ('unknown', None))
            m = re.search(r'\s([0-9\.]+)\s*kW', tr)
            if m:
                output = float(m.group(1))
                if socket == 'sev1011_t13':
                    # 230 V * 16 A = 3.68 kW
                    if output > 2.3 and output <= 3.7:
                        socket, voltage = 'sev1011_t23', 230
                    # 400 V * 16 A = 6.4 kW
                    if output > 3.7:
                        socket, output, voltage = 'sev1011_t25', min(output, 6.4), 400
                max_output[socket] = max(max_output.get(socket, 0.0), output)
            num_sockets[socket] = num_sockets.get(socket, 0) + 1
            if voltage:
                max_voltage[socket] = max(max_voltage.get(socket, 0), voltage)
    tags = {}
    for socket, count in num_sockets.items():
        tags['socket:%s' % socket] = str(count)
        output = max_output.get(socket, 0.0)
        if output > 0.0:
            output = str(int(output)) if output == int(output) else str(output)
            tags['socket:%s:output' % socket] = '%s kW' % output
        voltage = max_voltage.get(socket, 0)
        if voltage > 0:
            tags['socket:%s:voltage' % socket] = str(voltage)
    return tags


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
    if ref.startswith('CH*ECUE'):  # eCarUp
        return ref[7:]
    if ref.startswith('CH*SWIEE'):  # Swisscharge
        return str(int(ref[8:]))
    return ref
