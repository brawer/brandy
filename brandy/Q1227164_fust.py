# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Fust, Swiss retail chain
# https://www.wikidata.org/wiki/Q1227164

import html, json, re, requests


def main():
    features = fetch()
    j = json.dumps(features, sort_keys=True, indent=2, ensure_ascii=False)
    print(j)


def fetch():
    hdr = {'User-Agent': 'BrandBot/1.0'}
    page = requests.get('https://www.fust.ch/de/filialensuche.html', hdr).text
    lines = re.findall(r'<div class="item hasselectbutton.+? data-lng=.+?>', page)
    branches = [extract(line) for line in lines]
    branches = sorted(branches, key=lambda b: b["properties"]["ref"])
    return {
        "type": "FeatureCollection",
        "features": branches
    }


def extract(line):
    ref = int(re.search(r"data-id='(\d+)'", line)[1])
    lat = round(float(re.search(r'data-lat="([0-9.]+)"', line)[1]), 6)
    lng = round(float(re.search(r'data-lng="([0-9.]+)"', line)[1]), 6)
    text = re.search(r'''data-text=".+Fust(.+)<a''', line)[1]
    addr = [html.unescape(a) for a in text.split('<br/>') if a]
    postcode, city = addr[-1].split(' ', 1)
    props = {
        "addr:postcode": postcode,
        "addr:city": city,
        "brand": "Fust",
        "brand:wikidata": "Q1227164",
        "name": "Fust",
        "ref": ref
    }
    s = re.search(r'^(.+) (\d+)$', addr[-2])
    if s:
        props["addr:street"], props["addr:housenumber"] = s[1], s[2]
    else:
        props["addr:street"] = addr[-2]
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lng, lat]},
        "properties": props
    }


if __name__ == '__main__':
    main()
