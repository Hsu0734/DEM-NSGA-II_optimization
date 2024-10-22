'''
Read DEM data
Author: Hanwen Xu
Date: Jul 17, 2023
'''

import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

# read and print the DEM data
path_00 = '../00_data_source/Hanwen_10m.tif'
data_00 = rs.open(path_00)
# print(show(data_00, title='DTM_1km_6177_722'))


# creat a plot
fig, ax = plt.subplots(figsize=(16, 16))
show(data_00, title='DEM_demo', ax=ax)

plt.ticklabel_format(style='plain')
ax.tick_params(axis='both', which='major', labelsize=20)
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法

# grid and show plot
ax.grid(True, linestyle='--', color='grey')
plt.show()