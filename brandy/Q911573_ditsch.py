# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Ditsch bakery chain, https://www.wikidata.org/wiki/Q911573

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q911573')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
