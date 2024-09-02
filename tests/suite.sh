#!/usr/bin/env bats

SHAPELY="python -m src.shapely_cli.cli"

# The environment variable GREAT_LAKES_INPUT_FILE must be set when
# invoking this test script.

function assert_eq {
  if ! test "$1" == "$2"; then
    echo 'left: ' "$1"; echo 'right:' "$2"; return 1
  fi
}

@test "compute area for each feature" {
  run $SHAPELY 'geodesic_area(geom)' < $GREAT_LAKES_INPUT_FILE

  assert_eq $(echo "$output" | paste -s -d '+' - | bc) "244987543175.028322"
}

@test "assign area to property of each feature" {
  run $SHAPELY 'feature["properties"]["area"] = geodesic_area(geom)' < $GREAT_LAKES_INPUT_FILE

  assert_eq $(echo "$output" | jq 'select(.properties.name == "Lake Superior") | .properties.area') "82310839191.77948"
}

@test "compute bounds for each feature" {
  run $SHAPELY 'bounds(geom)' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | head -1)" "[-92.11418, 46.42339, -84.35621, 49.02763]"
}

@test "assign bbox to each feature" {
  run $SHAPELY 'feature["bbox"] = bounds(geom)' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | jq -c 'select(.properties.name == "Lake Superior") | .bbox')" \
    "[-92.11418,46.42339,-84.35621,49.02763]"
}

@test "compute bounds for entire feature collection" {
  run $SHAPELY 'bounds(union_all(geoms))' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$output" "[-92.11418, 41.39359, -75.7702, 49.02763]"
}

@test "find the largest feature in the collection (by area)" {
  run $SHAPELY 'max(features, key=lambda f: geodesic_area(f["geometry"]))' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | jq -r '.properties.name')" "Lake Superior"
}

@test "delete small features from the collection" {
  run $SHAPELY 'feature = feature if geodesic_area(geom) > 5e10 else None' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo $output | jq -cs '[.[].properties.name]')" '["Lake Superior","Lake Michigan","Lake Huron"]'
}

@test "delete every feature (useless but valid)" {
  run $SHAPELY 'del feature' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$output" ''
}

@test "delete every feature (useless but valid) [method 2]" {
  run $SHAPELY 'feature = None' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$output" ''
}

@test "null out geometry of every feature (also pretty useless)" {
  run $SHAPELY 'del geom' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | jq -cs '[.[].geometry]')" '[null,null,null,null,null]'
}

@test "null out geometry of every feature (also pretty useless) [method 2]" {
  run $SHAPELY 'geom = None' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | jq -cs '[.[].geometry]')" '[null,null,null,null,null]'
}

@test "simplify great lakes geojson" {
  run $SHAPELY 'simplify(geom, tolerance=0.05)' < $GREAT_LAKES_INPUT_FILE

  # TODO: better assertion
  test $(echo "$output" | wc -c) -lt $(echo "$(wc -c < $GREAT_LAKES_INPUT_FILE) / 2" | bc)
}

@test "union great lakes geojson" {
  run $SHAPELY 'union_all(geoms)' < $GREAT_LAKES_INPUT_FILE

  assert_eq "$(echo "$output" | wc -l)" 1
}
