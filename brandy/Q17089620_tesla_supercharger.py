# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Tesla Supercharger, charging stations for electric vehicles
# https://www.wikidata.org/wiki/Q17089620

import json
import ch_bfe_charging_stations


if __name__ == '__main__':
    # TODO: Find a feed for Tesla Superchargers with world-wide coverage.
    # Currently, we get only sites for superchargers located in Switzerland,
    # via the Swiss Federal Office of Energy who publishes a cross-brand feed
    # as Open Data.
    f = ch_bfe_charging_stations.load('Q17089620')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
