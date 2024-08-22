import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('Hanwen_3m_mask_shape.tif')
mask = wbe.new_raster(dem.configs)

for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        elev = dem[row, col]
        if elev == dem.configs.nodata:
            mask[row, col] = dem.configs.nodata # Write the cell value of a Raster
        elif elev != dem.configs.nodata:
            mask[row, col] = 1.0

wbe.write_raster(mask, 'Hanwen_3m_mask.tif', compress=True)

