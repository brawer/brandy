# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

from brandy import create_app

def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing
