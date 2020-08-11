import numpy
from matplotlib import pyplot
from matplotlib import collections
from mpl_toolkits.basemap import Basemap

def get_map_projection(src):
    """
    Return map projection specific to source.
    """
    # extract rupture enclosing polygon (considering a buffer of 10 km)
    rup_poly = src.polygon.dilate(10)
    min_lon = numpy.min(rup_poly.lons)
    max_lon = numpy.max(rup_poly.lons)
    min_lat = numpy.min(rup_poly.lats)
    max_lat = numpy.max(rup_poly.lats)
    
    # create map projection
    m = Basemap(projection='merc', llcrnrlat=min_lat, urcrnrlat=max_lat,
                llcrnrlon=min_lon, urcrnrlon=max_lon, resolution='l')

    return min_lon, max_lon, min_lat, max_lat, m

def get_mesh_boundary(mesh):
    """
    Return coordinates of mesh boundary
    """
    boundary_lons = numpy.concatenate((mesh.lons[0, :], mesh.lons[1:, -1], mesh.lons[-1,:-1][::-1], mesh.lons[:-1, 0][::-1]))
    boundary_lats = numpy.concatenate((mesh.lats[0, :], mesh.lats[1:, -1], mesh.lats[-1,:-1][::-1], mesh.lats[:-1, 0][::-1]))
    
    return boundary_lons, boundary_lats

def get_fault_plot(src):
     # loop over ruptures, extract rupture surface boundary and magnitude
    min_lon, max_lon, min_lat, max_lat, m = get_map_projection(src)

    boundaries = []
    mags = []

    for rup in src.iter_ruptures():
        surf = rup.surface
        mesh = surf.mesh
        mag = rup.mag

        boundary_lons, boundary_lats = get_mesh_boundary(mesh)
        xx, yy = m(boundary_lons, boundary_lats)

        boundaries.append([(x, y) for x, y in zip(xx, yy)])
        mags.append(mag)

    boundaries = numpy.array(boundaries)
    mags = numpy.array(mags)

    unique_mags = numpy.unique(mags)
    for mag in unique_mags:
        idx = mags == mag
        fig = pyplot.figure(figsize=(9, 9), dpi=160)

        m.drawparallels(numpy.arange(min_lat, max_lat, 0.2), labels=[True, False, False, True])
        m.drawmeridians(numpy.arange(min_lon, max_lon, 0.2), labels=[True, False, False, True])
        m.drawcoastlines()
        m.drawcountries()

        # extract and plot fault trace
        lons = [p.longitude for p in src.fault_trace.points]
        lats = [p.latitude for p in src.fault_trace.points]
        x, y = m(lons, lats)
        m.plot(x, y, linewidth=2, color='black')

        nl = []
        for i in boundaries[idx]:
            for j in i:
                nl.append([j[0],j[1]])

        bounds = collections.PolyCollection([nl], facecolors='palegreen')
        pyplot.gca().add_collection(bounds)


        pyplot.title('Simple Fault Source Ruptures, M=%s' % mag, fontsize=20)