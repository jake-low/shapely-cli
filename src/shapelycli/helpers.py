import pyproj
import numpy

wgs84 = pyproj.Geod(ellps="WGS84")

def geodesic_length(geom):
    return wgs84.geometry_length(geom)

def geodesic_area(geom):
    return abs(wgs84.geometry_area_perimeter(geom)[0])

def geodesic_perimeter(geom):
    return wgs84.geometry_area_perimeter(geom)[1]


def proj(from_crs, to_crs):
    if type(from_crs) is int:
        from_crs = "EPSG:" + str(from_crs)
    if type(to_crs) is int:
        to_crs = "EPSG:" + str(to_crs)

    transformer = pyproj.Transformer.from_crs(pyproj.CRS(from_crs), pyproj.CRS(to_crs), always_xy=True)
    def wrapper(coords):
        new_coords = transformer.transform(coords[:, 0], coords[:, 1])
        return numpy.array(new_coords).T
    
    return wrapper
