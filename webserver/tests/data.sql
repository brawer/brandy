/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Test data for Brandy unittests
 */

INSERT INTO scrape (id, scraper, num_features, error_log)
VALUES
  (17, 'Q860_foobar.py', 821, ""),
  (23, 'Q1568346_test.py', 0, "error log");
