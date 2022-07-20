# SPDX-License-Identifier: MIT

import csv, ftplib, io, json, re


def main():
    with open('keys/Q692400.json') as f:
        secrets = json.load(f)
    feed = convert(fetch(secrets))
    # feed = convert(open('Export_Geodaten_APP.csv', 'rb').read())
    print(json.dumps(feed, sort_keys=True, indent=2, ensure_ascii=False))


def fetch(secrets):
    data = io.BytesIO()
    with ftplib.FTP('remote.mobility.ch') as ftp:
        ftp.login(user=secrets['username'], passwd=secrets['password'])
        ftp.retrbinary('RETR Export_Geodaten_APP.csv',
                        callback=lambda b: data.write(b))
    return data.getvalue()


def convert(data):
    # Data is in ISO-8859-1 encoding, but sometimes it uses
	# U+0092 PRIVATE USE TWO for the apostrophe character.
    data_u = data.decode('iso-8859-1')
    data_u = data_u.replace('\u0092', '\u2019')
    lines = data_u.splitlines()
    features = {}
    for row in csv.DictReader(lines, delimiter=';', quoting=csv.QUOTE_NONE):
        r = extract(row)
        ref = r['properties']['ref']
        if ref in features:
            features[ref]['properties'].update(r['properties'])
        else:
            features[ref] = r
    features = sorted(features.values(),
                      key=lambda f: int(f['properties']['ref']))
    for f in features:
        fix_descriptions(f)
    return {
        'type': 'FeatureCollection',
        'features': features
    }


def extract(row):
    lng, lat = round(float(row['Laenge']), 6), round(float(row['Breite']), 6)
    lang = [None, 'de', 'fr', 'it', 'en'][int(row['Sprache'])]
    postcode = int(row['StaoPLZ'])
    country = 'LI' if postcode >= 9485 and postcode <= 9499 else 'CH'
    props = {
        'addr:city': row['Ortschaft'],
        'addr:postcode': str(postcode),
        'addr:country': country,
        'amenity': 'car_sharing',
        'operator': 'Mobility',
        'operator:wikidata': 'Q692400',
        'description:%s' % lang: row['Beschreibung'].strip(),
        'ref': row['Id'].strip(),
    }
    props.update(split_address(row['Adresse']))
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "properties": props,
    }


def split_address(a):
    a = {
        'Oberdorfstrasse 2 / Haus D': 'Oberdorfstrasse 2d',
    }.get(a, a).strip()
    p = a.split()
    if len(p) == 0:
        return {'noaddress': 'yes'}

    # "Bahnhofplatz 2" --> ("Bahnhofplatz", "2")
    if len(p) >= 2 and p[-1].isnumeric():
        return {
            'addr:housenumber': p[-1],
            'addr:street': ' '.join(p[:-1]),
        }

    # "Rigistrasse 171 b" --> ("Rigistrasse", "171b")
    if len(p) >= 3 and p[-2].isnumeric() and len(p[-1]) == 1:
        return {
            'addr:housenumber': ''.join(p[-2:]).lower(),
            'addr:street': ' '.join(p[:-2]),
        }

    # "Pilatusstrasse 46a", "Zentralstrasse 14B"
    if len(p) >= 2 and re.match(r'\d+[a-zA-Z]', p[-1]):
        return {
            'addr:housenumber': p[-1].lower(),
            'addr:street': ' '.join(p[:-1]),
        }

    # "Tüffenwies 33-C" --> ("Tüffenwies", "33c")
    if len(p) >= 2 and re.match(r'\d+-[a-zA-Z]', p[-1]):
        return {
            'addr:housenumber': p[-1].replace('-', '').lower(),
            'addr:street': ' '.join(p[:-1]),
        }

    # "Zumhofstrasse 1-3" --> ("Zumhofstrasse", "1-3")
    if len(p) >= 2 and re.match(r'\d+-\d+', p[-1]):
        return {
            'addr:housenumber': p[-1],
            'addr:street': ' '.join(p[:-1]),
        }

    # "Wesemlinrain 10+24" --> ("Wesemlinrain", "10;24')
    if len(p) >= 2 and re.match(r'\d+[+]\d+', p[-1]):
        return {
            'addr:housenumber': p[-1].replace('+', ';'),
            'addr:street': ' '.join(p[:-1]),
        }

    # "Limmattalstrasse 5/7" --> ("Limmattalstrasse", "5;7")
    if len(p) >= 2 and re.match(r'\d+[/]\d+', p[-1]):
        return {
            'addr:housenumber': p[-1].replace('/', ';'),
            'addr:street': ' '.join(p[:-1]),
        }

    if a in {'Aarepark', 'Bahnhof', 'Bahnhof Stettbach', 'Bahnhofareal',
             'EuroAirport'} or ('Parkhaus' in p) or ('Parking' in p):
        return {
            'addr:place': ' '.join(p),
            'nohousenumber': 'yes',
        }

    return {
        'addr:street': ' '.join(p),
        'nohousenumber': 'yes',
    }


def fix_descriptions(f):
    """Remove multilingual descriptions that are just untranslated,
    verbatim copies."""
    props = f['properties']
    local_lang = local_language(int(props['addr:postcode']))
    local_desc = props.get('description:%s' % local_lang)
    for lang in ['de', 'fr', 'it', 'en']:
        lang_key = 'description:%s' % lang
        if lang != local_lang and props.get(lang_key) == local_desc:
            del props[lang_key]


def local_language(postcode):
    """Find the language for a Swiss postcode, such as 'de' for 8952."""
    if postcode in {2533, 3960}:  # 2533 Evilard, 3960 Sierre
        return 'fr'
    if postcode < 2500 or postcode >= 2600 and postcode <= 2999:
        return 'fr'
    if postcode >= 6500 and postcode <= 6999:
        return 'it'
    return 'de'


if __name__ == '__main__':
    main()
