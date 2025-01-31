#!/bin/sh

# run suite twice, once for GeoJSON and once for NDJSON
env GREAT_LAKES_INPUT_FILE="tests/great-lakes.geojson" bats $@ tests/suite.sh
env GREAT_LAKES_INPUT_FILE="tests/great-lakes.ndjson" bats $@ tests/suite.sh

# run one more time, on a compact (not pretty printed) version of the GeoJSON
jq -c < tests/great-lakes.geojson > tests/great-lakes.compact.geojson
env GREAT_LAKES_INPUT_FILE="tests/great-lakes.compact.geojson" bats $@ tests/suite.sh
rm tests/great-lakes.compact.geojson
