# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# "U-Store" convenience stores, https://www.wikidata.org/wiki/Q113290511

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q113290511')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
