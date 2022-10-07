# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
#
# Setup when building a container for production; used by Containerfile.

from pathlib import Path
from setuptools import find_packages, setup

def _parse_requirements(filename):
    reqs = []
    with open(Path(__file__).parent / filename) as f:
        for line in f:
            line = line.strip()
            if line and not line[0] == '#':
                reqs.append(line)
    return reqs


setup(
    name='brandy',
    use_scm_version={'root': '..'},
    packages=find_packages(),
    include_package_data=True,
    install_requires=_parse_requirements('requirements.txt'),
    setup_requires=['setuptools_scm'],
)
