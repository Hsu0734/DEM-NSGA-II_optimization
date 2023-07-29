'''
Whitebox tool
Objective: solution plot
Author: Hanwen Xu
Version: 1
Date: Jul 29, 2023
'''

import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show, show_hist
import matplotlib.pyplot as plt

# whitebox default setting
wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'

# creat the flow_accum plot
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(36, 12))

# read image loop
for i in range(10):
    filename = f'DEM_after_{10 * i}.tif'
    dem = wbe.read_raster(file_name=filename)  # read the DEM

    flow_accum = wbe.d8_flow_accum(dem)   # d8_analysis
    flow_filename = f'DEM_flow_accum_{10 * i}.tif'
    wbe.write_raster(flow_accum, file_name=flow_filename, compress=True)

    path = rf"DEM_flow_accum_{10 * i}.tif"
    data = rs.open(path)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    show(data, title=f'DEM_flow_accum_{10 * i}', ax=axes[row, col])
    axes[row, col].set_title(f'DEM_flow_accum_{10 * i}')
    axes[row, col].axis('on')
    axes[row, col].ticklabel_format(style='plain')
    axes[row, col].grid(True, linestyle='--', color='black')

cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.7])  # 调整colorbar位置和大小
cbar = plt.colorbar(axes[0, 0].images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=12)
# plt.tight_layout()
plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM flow accumulation figure", fontsize=30)
plt.show()



#----------------------#
# creat the path length plot
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(36, 12))

# read image loop
for i in range(10):
    flow_filename = f'DEM_flow_accum_{10 * i}.tif'
    dem_02 = wbe.read_raster(file_name=flow_filename)
    path_length = wbe.new_raster(dem_02.configs)
    for row in range(dem_02.configs.rows):
        for col in range(dem_02.configs.columns):
            elev = dem_02[row, col] # Read a cell value from a Raster
            if elev >= 83.0 and elev != dem_02.configs.nodata:
                path_length[row, col] = 1.0 # Write the cell value of a Raster
            elif elev == dem_02.configs.nodata:
                path_length[row, col] = dem_02.configs.nodata
            elif elev < 83.0:
                path_length[row, col] = 0.0

    wbe.write_raster(path_length, f'DEM_path_length_{10 * i}.tif', compress=True)

    path_02 = rf"DEM_path_length_{10 * i}.tif"
    data_02 = rs.open(path_02)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    show(data_02, title=f'DEM_path_length_{10 * i}', ax=axes[row, col])
    axes[row, col].set_title(f'DEM_path_length_{10 * i}')
    axes[row, col].axis('on')
    axes[row, col].ticklabel_format(style='plain')
    axes[row, col].grid(True, linestyle='--', color='black')

# plt.tight_layout()
plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM path length figure", fontsize=30)
plt.show()