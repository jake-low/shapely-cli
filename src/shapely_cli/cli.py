import click
import json
import shapely
import sys
import traceback

from .eval import evaluate

def read_features_from_file(file):
    """
    Reads a file and yields GeoJSON features from it. Automatically detects
    whether the file is a single GeoJSON FeatureCollection or an NDJSON file
    with one feature on each line.
    """
    first_line = file.readline()
    is_ndjson = True

    # try parsing the first line as a complete GeoJSON object
    try:
        geojson = json.loads(first_line)
    except json.decoder.JSONDecodeError:
        # if that fails, read the rest of the file and attemp to parse
        # the whole thing as one JSON document
        is_ndjson = False
        remaining = file.read()
        geojson = json.loads(first_line + remaining)

    if geojson.get('type') == 'FeatureCollection':
        # NOTE: if the first feature is a FeatureCollection, we assume it's the only feature,
        # even if it was read all from a single line. This means we don't support the case
        # of an NDJSON file containing one FeatureCollection per line (only the first feature
        # would be processed).
        is_ndjson = False
        yield from geojson['features']
    else:
        yield geojson

    if is_ndjson:
        # read and yield the rest of the features in the NDJSON stream
        for line in file:
            yield json.loads(line)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, val):
        # if isinstance(val, numpy.ndarray):
        #     # TODO: can we somehow ensure that all elements in the array
        #     # are printed with the same numerical precision?
        #     pass
            
        # convert iterables to JSON arrays
        try:
            iterable = iter(val)
        except TypeError:
            pass
        else:
            return list(iterable)
        
        # convert shapely Geometries to GeoJSON
        if isinstance(val, shapely.Geometry):
            return shapely.geometry.mapping(val)

        # delegate to base class for other types
        return super().default(val)

import ast

@click.command()
@click.version_option(package_name="shapely_cli", prog_name="shapely-cli")
@click.argument("expr", metavar="EXPRESSION")
def main(expr: str):
    parsed = ast.parse(expr)
    names = [ node.id for node in ast.walk(ast.parse(expr)) if isinstance(node, ast.Name) ]

    if 'features' in names or 'geoms' in names:
        # evaluate expression once on all input features
        features = list(read_features_from_file(sys.stdin))
        if not features:
            return
        if len(features) == 1 and features[0]["type"] == "FeatureCollection":
            # TODO: handle geometry collections
            # TODO: expose collection object as a local when evaluating expr
            features = features[0]["features"]

        for feature in features:
            feature["geometry"] = shapely.geometry.shape(feature["geometry"])
        
        geoms = [feature["geometry"] for feature in features]

        locals = { "geoms": geoms, "features": features }
        try:
            (has_retval, retval) = evaluate(expr, locals)
        except BaseException as e:
            traceback.print_exception(e, limit=0, file=sys.stderr)
            exit(1)

        if has_retval:
            res = retval
        elif feature or geom:
            res = feature or geom
        else:
            res = None
        
        if res is not None:
            print(json.dumps(res, cls=CustomJSONEncoder))

        return

    # else
    
    for feature in read_features_from_file(sys.stdin):
        if 'geometry' in feature:
            geom = shapely.geometry.shape(feature['geometry'])
        else:
            geom = shapely.geometry.shape(feature)
            feature = None

        # evaluate the user-provided expression on the geometry
        locals = { "geom": geom, "feature": feature }
        try:
            (has_retval, retval) = evaluate(expr, locals)
        except BaseException as e:
            traceback.print_exception(e, limit=0, file=sys.stderr)
            exit(1)

        # expr is allowed to modify feature or geom, so get new values
        feature = locals.get("feature")
        geom = locals.get("geom")

        if feature:
            # in case geom was modified, update feature["geometry"] to match
            feature["geometry"] = geom
        else:
            # expr either did 'feature = None' or 'del feature';
            # remove the geom too (so it isn't printed instead)
            geom = None

        if has_retval:
            res = retval
        elif feature or geom:
            res = feature or geom
        else:
            res = None
        
        if res is not None:
            print(json.dumps(res, cls=CustomJSONEncoder))
            
if __name__ == "__main__":
    # only executed when running without installing, i.e. python -m src.shapely_cli.cli
    # (which is used by the unit test scripts)
    main()
