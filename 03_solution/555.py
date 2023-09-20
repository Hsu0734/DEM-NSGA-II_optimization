import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

# Read and print the DEM data
path_00 = '../03_solution/balance_solution.tif'
data_00 = rs.open(path_00)

# Read the DEM data into a NumPy array
dem_array = data_00.read(1, masked=True)  # 使用 masked=True 来自动处理 nodata 值

# Calculate the minimum and maximum elevation values, excluding nodata
min_elevation = np.min(dem_array[~dem_array.mask])
max_elevation = np.max(dem_array[~dem_array.mask])

# Create a plot
fig, ax = plt.subplots(figsize=(24, 24))

# Use imshow to display the DEM data with the correct color mapping
image = ax.imshow(dem_array, vmin=min_elevation, vmax=0.8)
show(data_00, ax=ax)

# Create a colorbar
cbar = plt.colorbar(image, ax=ax, orientation='vertical', shrink=0.3)
cbar.set_label('Elevation (meters)')

plt.ticklabel_format(style='plain')
# ax.grid(True, linestyle='--', color='grey')
plt.show()
