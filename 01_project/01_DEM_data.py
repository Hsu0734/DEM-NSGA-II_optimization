'''
Read DEM data
Author: Hanwen Xu
Date: Jul 17, 2023
'''

import rasterio as rs
from rasterio.plot import show

# read and print the DEM data
path_00 = '../00_data_source/SIMRAIN_1km_6175_727.tif'
data_00 = rs.open(path_00)
print(show(data_00, cmap='winter', title='DEM_small'))