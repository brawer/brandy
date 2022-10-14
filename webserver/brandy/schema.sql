/* SPDX-License-Identifier: MIT
 * SPDX-FileCopyrightText: 2022 Sascha Brawer <sascha@brawer.ch>
 *
 * Database schema for Brandy webserver
 */

DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS scrape;
DROP TABLE IF EXISTS scraper;
DROP TABLE IF EXISTS brand;
DROP TABLE IF EXISTS brand_feature;

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
  last_checked TIMESTAMP NOT NULL,
  last_modified TIMESTAMP,
  min_lng REAL NOT NULL,
  min_lat REAL NOT NULL,
  max_lng REAL NOT NULL,
  max_lat REAL NOT NULL
);

CREATE TABLE brand_feature (
  internal_id INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_id INT8 NOT NULL,
  feature_id TEXT NOT NULL,
  lng REAL NOT NULL,
  lat REAL NOT NULL,
  hash_hi INT8 NOT NULL,
  hash_lo INT8 NOT NULL,
  last_modified TIMESTAMP NOT NULL,
  props BLOB NOT NULL
);

CREATE VIRTUAL TABLE brand_feature_rtree USING rtree(
   internal_id,
   min_lng, max_lng,
   min_lat, max_lat,
   +brand_id INT8
);
