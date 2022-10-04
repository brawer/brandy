/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Database schema for Brandy webserver
 */

DROP TABLE IF EXISTS scrape;
DROP TABLE IF EXISTS brand;

CREATE TABLE scrape (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  scraper TEXT NOT NULL,
  num_features INT NOT NULL,
  error_log TEXT
);

CREATE TABLE brand (
  wikidata_id INTEGER PRIMARY KEY NOT NULL,
  last_scrape_id INTEGER NOT NULL,
  FOREIGN KEY (last_scrape_id) REFERENCES scrape (id)
);
