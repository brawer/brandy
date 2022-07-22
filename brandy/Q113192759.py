# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# eCarUp, charging stations for electric vehicles, Switzerland
# https://www.wikidata.org/wiki/Q113192759

import json
import ch_bfe_charging_stations


if __name__ == '__main__':
    f = ch_bfe_charging_stations.load('Q113192759')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
