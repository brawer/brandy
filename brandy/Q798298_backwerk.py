# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# BackWerk bakery chain, https://www.wikidata.org/wiki/Q798298

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q798298')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
