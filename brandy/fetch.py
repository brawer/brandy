# SPDX-License-Identifier: MIT

import os, subprocess, time
from hashlib import sha1


def chains():
    dirname = os.path.dirname(__file__)
    chains = [d.split('.')[0].upper() for d in os.listdir(dirname)
		      if d.startswith('Q') and d.endswith('.py')]
    return sorted(chains, key=lambda q:int(q[2:]))


def fetch_chain(chain):
    dirname = os.path.join('public_html', chain)
    timestamp = time.strftime("%Y-%d-%mT%H:%M:%SZ", time.gmtime())
    os.makedirs(dirname, exist_ok=True)
    versions = sorted([os.path.join(dirname, f) for f in os.listdir(dirname)
                       if f.endswith('.geojson')])
    if len(versions) > 0:
        with open(versions[-1], 'rb') as f:
            prev_content = f.read()
    else:
        prev_content = b''

    p = subprocess.run(args=['python3', 'brandy/brandy/%s.py' % chain],
                       capture_output=True, encoding='utf8', timeout=60)
    with open(os.path.join(dirname, 'log.txt'), 'w') as log:
        if p.returncode == 0 and p.stdout != prev_content:
            encoded = p.stdout.encode('utf-8')
            if encoded != prev_content:
                filename = os.path.join(dirname, '%s.geojson' % timestamp)
                with open(filename, 'w') as f:
                    f.write(p.stdout)
            log.write('Content-Length: %s\n' % len(encoded))
            log.write('Content-SHA1: %s\n' % sha1(encoded).hexdigest())
        log.write('Date: %s\n' % timestamp)
        if p.stderr:
            log.write('\n')
            log.write(p.stderr)


if __name__ == '__main__':
    for c in chains():
        fetch_chain(c)
