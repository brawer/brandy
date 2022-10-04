/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Database schema for Brandy webserver
 */

DROP TABLE IF EXISTS scrape;
DROP TABLE IF EXISTS scraper;
DROP TABLE IF EXISTS brand;

CREATE TABLE scraper (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT UNIQUE NOT NULL
);

CREATE TABLE scrape (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  scraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  scraper_id INTEGER NOT NULL,
  num_features INTEGER NOT NULL,
  error_log TEXT,
  FOREIGN KEY (scraper_id) REFERENCES scraper (id)
);

CREATE TABLE brand (
  wikidata_id INT8 PRIMARY KEY NOT NULL,
  last_scrape_id INTEGER NOT NULL,
  FOREIGN KEY (last_scrape_id) REFERENCES scrape (id)
);
