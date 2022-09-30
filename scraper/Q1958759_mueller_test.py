# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>

import unittest

from .Q1958759_mueller import convert_street

class TestConvertStreet(unittest.TestCase):
    def test_basic(self):
        self.assertEqual({
            'addr:housenumber': '11',
            'addr:street': 'Karlsplatz'
        }, convert_street({'street': 'Karlsplatz 11'}))
        self.assertEqual({
            'addr:housenumber': '4',
            'addr:street': 'Bergheimer Str.'
        }, convert_street({'street': 'Bergheimer Str.4'}))

    def test_housenumber_with_letter(self):
        self.assertEqual({
            'addr:housenumber': '11a',
            'addr:street': 'Karlsplatz'
        }, convert_street({'street': 'Karlsplatz 11a'}))
        self.assertEqual({
            'addr:housenumber': '31A',
            'addr:street': 'Svilajska'
        }, convert_street({'street': 'Svilajska 31 A'}))
        self.assertEqual({
            'addr:housenumber': '68/a',
            'addr:street': 'Siklósi út'
        }, convert_street({'street': 'Siklósi út 68/a'}))

    def test_housenumber_range(self):
        self.assertEqual({
            'addr:housenumber': '11-13',
            'addr:street': 'Karlsplatz'
		}, convert_street({'street': 'Karlsplatz 11-13'}))
        self.assertEqual({
            'addr:housenumber': '11-13',
            'addr:street': 'Karlsplatz'
		}, convert_street({'street': 'Karlsplatz 11 - 13'}))
        self.assertEqual({
            'addr:housenumber': '17/18',
            'addr:street': 'Kornmarkt'
		}, convert_street({'street': 'Kornmarkt 17/18'}))
        self.assertEqual({
            'addr:housenumber': '3;5',
            'addr:street': 'Brunngasse'
		}, convert_street({'street': 'Brunngasse 3+5'}))

    def test_place(self):
        self.assertEqual({
            'addr:place': 'City Arkaden'
        }, convert_street({'street': 'City Arkaden'}))

    def test_street_with_place(self):
        self.assertEqual({
            'addr:housenumber': '12',
            'addr:place': 'Szombathely Center',
            'addr:street': 'Viktória utca'
        }, convert_street({'street': 'Viktória utca 12 (Szombathely Center)'}))
        self.assertEqual({
            'addr:housenumber': '11-12',
            'addr:place': 'Stachus',
            'addr:street': 'Karlsplatz'
        }, convert_street({'street': 'Karlsplatz 11-12 (Stachus)'}))

    def test_nohousenumber(self):
        self.assertEqual({
            'nohousenumber': 'yes',
            'addr:street': 'Augsburger Straße'
        }, convert_street({'street': 'Augsburger Straße'}))
        self.assertEqual({
            'nohousenumber': 'yes',
            'addr:street': 'Straubinger Str.'
        }, convert_street({'street': 'Straubinger Str.'}))
        self.assertEqual({
            'nohousenumber': 'yes',
            'addr:street': 'Avinguda Juan Carlos I'
        }, convert_street({'street': 'Avinguda Juan Carlos I'}))


if __name__ == '__main__':
    unittest.main()
