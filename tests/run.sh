#!/bin/sh

# run suite twice, once for GeoJSON and once for NDJSON
env GREAT_LAKES_INPUT_FILE="tests/great-lakes.geojson" bats $@ tests/suite.sh
env GREAT_LAKES_INPUT_FILE="tests/great-lakes.ndjson" bats $@ tests/suite.sh
