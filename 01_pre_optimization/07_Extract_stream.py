import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
dem = wbe.read_raster('DEM_demo_d8.tif')

# slope analysis
streams = wbe.extract_streams(dem, threshold=7.18)
wbe.write_raster(streams, 'DEM_demo_extract_stream.tif', compress=True)



# visualization
path_03 = '../00_data_source/DEM_demo_extract_stream.tif'
data_03 = rs.open(path_03)

fig, ax = plt.subplots(figsize=(16, 16))
show(data_03, title='DEM_demo_basin', ax=ax)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True,  linestyle='--', color='grey')
plt.show()


# value
extract_stream = 0
for row in range(streams.configs.rows):
    for col in range(streams.configs.columns):
        elev = streams[row, col]
        if elev != streams.configs.nodata:
            extract_stream = extract_stream + 1

# print(Slope_value)
print(extract_stream)