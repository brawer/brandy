# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Avec kiosk chain, https://www.wikidata.org/wiki/Q103863974

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q103863974')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
