# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# "Press & Books" news agent, https://www.wikidata.org/wiki/Q100407277

import json
import com_valora_stores


if __name__ == '__main__':
    f = com_valora_stores.load('Q100407277')
    print(json.dumps(f, sort_keys=True, indent=2, ensure_ascii=False))
