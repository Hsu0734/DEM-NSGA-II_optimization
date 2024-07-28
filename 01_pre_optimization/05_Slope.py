import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('Hanwen_2m.tif')

# slope analysis
slope = wbe.slope(dem, units="percent")
wbe.write_raster(slope, 'DEM_demo_slope.tif', compress=True)



# visualization
path_03 = '../00_data_source/DEM_demo_slope.tif'
data_03 = rs.open(path_03)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_03, title='DEM_demo_slope', ax=ax)

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=20)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True,  linestyle='--', color='grey')

plt.show()


# value
Slope_value = []
for row in range(slope.configs.rows):
    for col in range(slope.configs.columns):
        elev = slope[row, col]
        if elev != slope.configs.nodata:
            Slope_value.append(elev)

# print(Slope_value)
print(max(Slope_value))
print(min(Slope_value))