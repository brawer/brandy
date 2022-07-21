# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Utilies for Swiss postal codes.


import csv, os, re, requests, time


_postcodes = {}  # 'worb' --> [3075, 3076, 3077, 3078]


def postcodes(city):
    """postcodes('Worb') --> [3075, 3076, 3077, 3078], or None"""
    if not _postcodes:
        _load()
    return _postcodes.get(city.lower())


def country(postcode):
    """country(8952) --> 'CH'; country(9490) --> 'LI'"""
    if postcode >= 9485 and postcode <= 9499:
        return 'LI'
    else:
        return 'CH'


def _load():
    os.makedirs('cache', exist_ok=True)
    path, age = os.path.join('cache', 'ch_postcodes.csv'), None
    try:
        age = time.time() - os.lstat(path).st_mtime
    except:
        pass
    if not age or age > 86400 * 7:  # 7 days in seconds
        with open(path + '.tmp', 'w') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Postcode', 'City'])
            for postcode, city in _fetch():
                writer.writerow([str(postcode), city])
        os.rename(path + '.tmp', path)
    with open(path, 'r') as csvfile:
        for row in csv.DictReader(csvfile):
            code = int(row['Postcode'])
            _postcodes.setdefault(row['City'].lower(), []).append(code)
    for c in _postcodes.values():
        c.sort()


def _fetch():
    endpoint = 'https://query.wikidata.org/sparql'
    query = '''SELECT ?postcode ?itemLabel WHERE {
      ?item wdt:P771 ?m; wdt:P281 ?postcode.
      SERVICE wikibase:label { bd:serviceParam wikibase:language "de,fr,it,en". }
    }'''
    r = requests.get(endpoint, params = {'format': 'json', 'query': query})
    data = r.json()
    p = []
    for r in r.json()['results']['bindings']:
        postcode = r['postcode']['value']
        if re.search(r'^\d{4}$', postcode):
            postcode = int(postcode)
        else:
            continue
        p.append((postcode, r['itemLabel']['value']))
    p.sort()
    return p
