import rasterio as rs
from rasterio.plot import show
import whitebox_workflows as wbw

# read and print the DEM data
path_00 = '../00_data_source/FloodingCPH.tif'
data_00 = rs.open(path_00)
print(show(data_00))

'''path_01 = '../00_data_source/min_earth_volume_solution.tif'
data_01 = rs.open(path_01)
print(show(data_01))

path_02 = '../00_data_source/min_flow_length_solution.tif'
data_02 = rs.open(path_02)
print(show(data_02))

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('min_velocity_solution.tif')

Flow_accum_value = []
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        elev = dem[row, col]
        if elev != dem.configs.nodata:
            print(elev)

path_01 = '../00_data_source/DEM_demo_resample.tif'
data_01 = rs.open(path_01)
print(show(data_01))'''