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
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(72, 48))

# read image loop
for i in range(20):
    filename = f'DEM_after_{10 * i}.tif'
    dem = wbe.read_raster(file_name=filename)  # read the DEM

    flow_accum = wbe.d8_flow_accum(dem, out_type='cells')   # d8_analysis
    slope = wbe.slope(dem, units="percent")
    velocity = wbe.new_raster(dem.configs)

    for row in range(slope.configs.rows):
        for col in range(slope.configs.columns):
            velo = slope[row, col]
            if velo == slope.configs.nodata:
                velocity[row, col] = slope.configs.nodata
            elif velo != slope.configs.nodata:
                slope_factor = (slope[row, col] / 100) ** 0.5
                flow_factor = (flow_accum[row, col] * 100 * 0.000004215717) ** (2 / 3)
                velocity[row, col] = (slope_factor * flow_factor / 0.03) ** 0.6


    flow_filename = f'DEM_velocity_{10 * i}.tif'
    wbe.write_raster(velocity, file_name=flow_filename, compress=True)

    path = rf"DEM_velocity_{10 * i}.tif"
    data = rs.open(path)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    show(data, cmap='Blues', title=f'DEM_velocity_{10 * i}', ax=axes[row, col])
    axes[row, col].set_title(f'DEM_velocity_{10 * i}')
    axes[row, col].axis('on')
    axes[row, col].ticklabel_format(style='plain')
    axes[row, col].grid(True, linestyle='--', color='black')

# plt.tight_layout()
plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM velocity figure", fontsize=30)
plt.savefig("All DEM velocity figure")
plt.show()