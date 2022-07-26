# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Brezelkönig, pretzel chain in Switzerland, Austria and Germany
# https://www.wikidata.org/wiki/Q111728604

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q111728604')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
