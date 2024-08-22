import rasterio as rs
from scipy.ndimage import binary_erosion
import numpy as np

# Load the DEM file
dem_3m_path = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source/Hanwen_3m.tif'
dem_3m_data = rs.open(dem_3m_path)
dem_3m_array = dem_3m_data.read(1)
nodata_3m_value = dem_3m_data.nodatavals[0]

# Shrink the valid data area by one pixel
valid_data_mask = (dem_3m_array != nodata_3m_value)
eroded_mask = binary_erosion(valid_data_mask, structure=np.ones((3, 3)))
modified_dem_3m_array = dem_3m_array.copy()
modified_dem_3m_array[~eroded_mask] = nodata_3m_value

# Save the modified DEM
output_path_3m_eroded = r'/00_data_source/Hanwen_3m_mask_shape.tif'
with rs.open(
    output_path_3m_eroded,
    'w',
    driver='GTiff',
    height=modified_dem_3m_array.shape[0],
    width=modified_dem_3m_array.shape[1],
    count=1,
    dtype=dem_3m_array.dtype,
    crs=dem_3m_data.crs,
    transform=dem_3m_data.transform,
    nodata=nodata_3m_value
) as dst:
    dst.write(modified_dem_3m_array, 1)
