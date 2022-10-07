/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Database schema for Brandy webserver
 */

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS scrape;
DROP TABLE IF EXISTS scraper;
DROP TABLE IF EXISTS brand;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  is_admin TINYINT NOT NULL DEFAULT 0
);

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
  scraped TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  min_lng_e7 INTEGER NOT NULL,
  min_lat_e7 INTEGER NOT NULL,
  max_lng_e7 INTEGER NOT NULL,
  max_lat_e7 INTEGER NOT NULL
);
