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
fig, axs = plt.subplots(2, 5, figsize=(12, 6))  # 创建一个 2 行 5 列的子图布局
plt.suptitle("All DEM flow accum figure")
plt.ticklabel_format(style='plain')  # 关闭科学计数法设置

# read image loop
for i in range(10):
    filename = f'DEM_after_{10 * i}.tif'
    dem = wbe.read_raster(file_name=filename)  # read the DEM

    flow_accum = wbe.d8_flow_accum(dem)   # d8_analysis
    flow_filename = f'DEM_flow_accum{10 * i}.tif'
    wbe.write_raster(flow_accum, file_name=flow_filename, compress=True)

    path = rf"DEM_flow_accum{10 * i}.tif"
    data = rs.open(path)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    axs[row, col].imshow(data.read(1))
    axs[row, col].set_title(f'solution{10 * i}')

plt.tight_layout()  # 调整子图布局，以免重叠
plt.show()



#----------------------#
# creat the path length plot
fig, axs = plt.subplots(2, 5, figsize=(12, 6))
plt.suptitle("All DEM path length figure")
plt.ticklabel_format(style='plain')

# read image loop
for i in range(10):
    flow_filename = f'DEM_flow_accum{10 * i}.tif'
    dem_02 = wbe.read_raster(file_name=flow_filename)
    path_length = wbe.new_raster(dem_02.configs)
    for row in range(dem_02.configs.rows):
        for col in range(dem_02.configs.columns):
            elev = dem_02[row, col] # Read a cell value from a Raster
            if elev >= 83.0 and elev != dem_02.configs.nodata:
                path_length[row, col] = 1.0 # Write the cell value of a Raster

            elif elev < 83.0 or elev == dem_02.configs.nodata:
                path_length[row, col] = 0.0
    wbe.write_raster(path_length, f'DEM_path_length{10 * i}.tif', compress=True)

    path_02 = rf"DEM_path_length{10 * i}.tif"
    data_02 = rs.open(path_02)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    axs[row, col].imshow(data_02.read(1))
    axs[row, col].set_title(f'solution{i}')

plt.tight_layout()  # 调整子图布局，以免重叠
plt.show()