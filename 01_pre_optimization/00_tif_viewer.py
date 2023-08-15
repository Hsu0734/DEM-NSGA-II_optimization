import rasterio as rs
from rasterio.plot import show

# read and print the DEM data
path_00 = '../00_data_source/DEM_demo_resample.tif'
data_00 = rs.open(path_00)
print(show(data_00))

'''path_01 = '../00_data_source/DEM_demo_resample.tif'
data_01 = rs.open(path_01)
print(show(data_01))'''