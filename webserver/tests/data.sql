/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Test data for Brandy unittests
 */

INSERT INTO scraper (id, name)
VALUES
  (1, 'Q860_foobar.py'),
  (2, 'Q1568346_test.py');

INSERT INTO scrape (id, scraper_id, num_features, error_log)
VALUES
  (17, 1, 821, ""),
  (23, 2, 0, "error log");
