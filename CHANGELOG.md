# Changelog

All notable changes to this project will be documented in this file.

Versioning of this project adheres to the [Semantic Versioning](https://semver.org/spec/v2.0.0.html) spec.

## [0.2.0]

- Fixed a bug where an input containing a GeoJSON FeatureCollection that was
  all on one line (not pretty-printed) would be treated as an NDJSON input,
  causing unexpected results: `feature` would refer to the entire collection
  rather than to a single element, as expected, and references to `geom` would
  crash since FeatureCollections don't have a `geometry` property.

## [0.1.1]

- Renamed package
- Fixed name of package shown in `--version` output
- Added install instructions to README

## [0.1.0]

Initial release.

[0.2.0]: https://github.com/jake-low/shapely-cli/releases/tag/v0.2.0
[0.1.1]: https://github.com/jake-low/shapely-cli/releases/tag/v0.1.1
[0.1.0]: https://github.com/jake-low/shapely-cli/releases/tag/v0.1.0
