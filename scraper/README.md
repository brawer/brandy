# Scraper

Once per day, the Brandy scraper fetches store locations from brand websites,
converts them to a standard format, and uploads the resulting file
to the Brandy webserver.


## Writing your own scraper

To set up a new development environment, run these commands:

```sh
git clone https://github.com/brawer/brandy.git
cd brandy
python3 -m venv venv
venv/bin/pip3 install -r scraper/requirements.txt
```

To support a new brand, look it up in the
[OpenStreetMap Name Suggestion Index (NSI)](https://nsi.guide/).
If your brand is not in NSI yet, please add it there first;
see [example](https://github.com/osmlab/name-suggestion-index/pull/7070/files).

Your scraper should fetch the data from the brand and emit
a [GeoJSON](https://en.wikipedia.org/wiki/GeoJSON) feature collection
with point features that carry OpenStreetMap tags as their properties.
Please make sure that your scraper emits
tags that do not conflict with NSI, otherwise you’ll
cause unnecessary work for OpenStreetMap editors.

For example, according to the
[NSI rules the Müller drugstore chain](https://nsi.guide/?id=muller-7b8da2),
the corresponding scraper should produce `brand=Müller`,
`brand:wikidata=Q1958759`,
`name=Müller`, and `shop=chemist`. To run the corresponding
scraper on your local machine, do this:

```sh
$ venv/bin/python3 scraper/Q1958759_mueller.py
```

You’ll see that the output is a feature collection of point features
whose properties are a superset of those in NSI.

To run the unit tests, do this:

```sh
$ venv/bin/python3 -m unittest scraper/*_test.py
```


