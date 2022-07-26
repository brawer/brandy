# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# "Service Store DB" convenience stores
# https://www.wikidata.org/wiki/Q84482517

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q84482517')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
