import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('Hanwen.tif')

# hydrological analysis
resample = wbe.resample(input_rasters=[dem], cell_size=2.0)
wbe.write_raster(resample, 'Hanwen_2m.tif', compress=True)



# visualization
path_01 = '../00_data_source/Hanwen_2m.tif'
data_01 = rs.open(path_01)

fig, ax = plt.subplots(figsize=(8, 8))
show(data_01, title='DEM_demo_resample', ax=ax)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True, linestyle='--', color='grey')
plt.show()