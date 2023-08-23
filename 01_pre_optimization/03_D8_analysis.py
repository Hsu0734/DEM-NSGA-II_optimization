import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('DEM_demo_resample_10m.tif')

# hydrological analysis
flow_accu = wbe.d8_flow_accum(dem, out_type='cells')

# flow_accu = wbe.watershed(depression)
wbe.write_raster(flow_accu, 'DEM_demo_d8.tif', compress=True)

# visualization
path_01 = '../00_data_source/DEM_demo_d8.tif'
data_01 = rs.open(path_01)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_01, title='DEM_demo_d8', ax=ax)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True, linestyle='--', color='grey')

# 添加颜色条
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)  # 使用 ax.images[0] 获取图像数据用于颜色条

# 调整颜色条上刻度标签的字体大小
cbar.ax.tick_params(labelsize=20)
plt.show()

# flow accumulation value
Flow_accum_value = []
for row in range(flow_accu.configs.rows):
    for col in range(flow_accu.configs.columns):
        elev = flow_accu[row, col]
        if elev != flow_accu.configs.nodata:
            Flow_accum_value.append(elev)

# print(Flow_accum_value)
print(max(Flow_accum_value))
print(min(Flow_accum_value))