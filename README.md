# Shapely CLI

A command line tool which wraps the [shapely] Python package (which in turn wraps [GEOS]), providing a convenient way to apply various operations to GeoJSON geometries from the command line.

## Examples

Say you have a GeoJSON file containing a single `FeatureCollection`, like [this one](./tests/great-lakes.geojson) which contains five features representing the five [Great Lakes](https://en.wikipedia.org/wiki/Great_Lakes) (each feature has some properties and a `Polygon` geometry).

Here are some things you could use `shapely-cli` to do.

Print the bounding boxes of each geometry:
```
$ shapely 'bounds(geom)' < great-lakes.geojson
[-92.11418, 46.42339, -84.35621, 49.02763]
[-88.04342, 41.62791, -84.77450, 46.11519]
[-79.77473, 43.19010, -75.77020, 44.50443]
[-83.46620, 41.39359, -78.86750, 43.10620]
[-84.78083, 43.01730, -79.66258, 46.35539]
```

Update each feature so that its geometry is guaranteed to be valid:
```
$ shapely 'geom = make_valid(geom)' < great-lakes.geojson
```

Add a bbox property to each feature:
```
$ shapely 'feature["bbox"] = bounds(geom)' < great-lakes.geojson
```

Produce a single MultiPolygon containing all of the input geometries:
```
$ shapely 'union_all(geoms)' < great-lakes.geojson
```

Find and print the feature with the largest area:
```
$ shapely 'max(features, key=lambda f: geodesic_area(f["geometry"]))' < great-lakes.geojson
```

Simplify each feature's geometry using [Ramer–Douglas–Peucker algorithm](https://en.wikipedia.org/wiki/Ramer–Douglas–Peucker_algorithm):
```
$ shapely 'geom = simplify(geom, tolerance=0.05)' < great-lakes.geojson
```

Reproject each feature from WGS 84 Lon/Lat to [Web Mercator coordinates](https://epsg.io/3857):
```
$ shapely 'geom = transform(geom, proj(4326, 3857))' < great-lakes.geojson
```

All of the above would also work if the input file were a newline-separated sequence of individual GeoJSON features, like [this](./tests/great-lakes.ndjson).

## How it works

The tool takes one argument which is a Python expression, statement, or series of statements (you can use semicolons to smush multiple statements into one line). It then reads a GeoJSON object or a newline-delimited sequence of GeoJSON objects (it automatically detects the difference) and applies the Python snippet to each feature or geometry in the input.

The Python snippet has access to the following variables:
- `feature` is the GeoJSON feature currently being processed
- `geom` is the GeoJSON geometry currently being processed (either a bare geometry or the one associated with the current `feature`)

In addition, everything from Shapely is in scope (via `from shapely import *`), as well as a few additional [helper functions](./src/shapelycli/helpers.py).

The Python snippet may end in an expression, in which case the result of that expression will be printed to STDOUT. Or, the Python snippet may be a statement (or series of statements) which modify `feature`, `geom`, or both. In this case each feature or geometry from STDIN is dumped back to STDOUT (with the modifications applied). If you wish to omit a feature from the output, use `feature = None` or `del feature`.

If the Python snippet refers to the variables `features` or `geoms` (in the plural), then instead of being run for each feature/geometry in the input, it will just be run once. `features` will be a list of all features in the input, and `geoms` will be a list of all geoms. This allows for aggregate operations like unioning all the geometries together, or finding the feature with the largest bounding box.

## Purpose

I work on geospatial software and do a lot of ad-hoc manipulation of geospatial data. I was finding myself frequently writing short Python scripts to transform GeoJSON data, like the following example:

```python
#!/usr/bin/env python3
"""
Add a bounding box to each feature in the input GeoJSON.
Usage: python add_bbox.py < input.geojson > output.geojson
"""
import sys
import json
import shapely

geojson = json.load(sys.stdin)
assert geojson.get("type") == "FeatureCollection"

for feature in geojson["features"]:
    geom = shapely.geometry.mapping(feature["geometry"])
    feature["bbox"] = shapely.bounds(geom)

json.dump(geojson, file=sys.stdout)
```

I wrote shapely-cli as an experiment to see if I could replace these single-purpose scripts with one-liners. So far I've found it to be moderately useful.

There are still missing features (for example, if the input is a FeatureCollection, it's not possible to access or modify the `properties` on that collection). And I'm honestly not sure yet if the approach I've taken (evaling Python snippets) is a good idea or not. Is it too magic? Or just the right amount?

If you decide to try out this tool, I'd love to hear your thoughts on it and how you're using it. Feel free to open an issue or email me.

[shapely]: https://shapely.readthedocs.io/en/stable/manual.html
[GEOS]: https://libgeos.org/
