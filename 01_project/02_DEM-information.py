import whitebox_workflows as wbw
from whitebox_workflows import PhotometricInterpretation, RasterDataType
import rasterio as rs
from rasterio.plot import show

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB'

# web read DEM data
dem = wbe.read_raster('DEM_Clip.tif')

# size and resolution
print(f'Rows: {dem.configs.rows}')
print(f'Columns: {dem.configs.columns}')
print(f'Resolution (x direction): {dem.configs.resolution_x}')
print(f'Resolution (y direction): {dem.configs.resolution_y}')

# coordinate location
print(f'North: {dem.configs.north}')
print(f'South: {dem.configs.south}')
print(f'East: {dem.configs.east}')
print(f'West: {dem.configs.west}')

# minimum and maximum value
print(f'Min value: {dem.configs.minimum}')
print(f'Max value: {dem.configs.maximum}')
print(f'Nodata value: {dem.configs.nodata}')

# each pixel data
Elevation = []
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        elev = dem[row, col]
        Elevation.append(elev)

print(Elevation)