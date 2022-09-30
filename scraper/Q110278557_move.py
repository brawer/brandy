# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Move, charging stations for electric vehicles
# https://www.wikidata.org/wiki/Q110278557

import json
import ch_bfe_charging_stations


if __name__ == '__main__':
    f = ch_bfe_charging_stations.load('Q110278557')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
