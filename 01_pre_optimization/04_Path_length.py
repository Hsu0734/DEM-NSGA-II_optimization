import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
flow_accum = wbe.read_raster('DEM_demo_d8.tif')
path_length = wbe.new_raster(flow_accum.configs)

for row in range(flow_accum.configs.rows):
    for col in range(flow_accum.configs.columns):
        elev = flow_accum[row, col] # Read a cell value from a Raster
        if elev >= 54.6 and elev != flow_accum.configs.nodata: #threshold: 2m_91.90; 3m_54.56; 5m_29.12; 10m_14.36
            path_length[row, col] = 1.0 # Write the cell value of a Raster

        elif elev < 54.6 and elev != flow_accum.configs.nodata:
            path_length[row, col] = 0.0

        elif elev == flow_accum.configs.nodata:
            path_length[row, col] = flow_accum.configs.nodata

wbe.write_raster(path_length, 'DEM_demo_path.tif', compress=True)


# visualization
path_02 = '../00_data_source/DEM_demo_path.tif'
data_02 = rs.open(path_02)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_02, title='DEM_demo_path', ax=ax)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True, linestyle='--', color='grey')

plt.show()


# value
Path_value = []
for row in range(path_length.configs.rows):
    for col in range(path_length.configs.columns):
        elev = path_length[row, col]
        if elev != path_length.configs.nodata:
            Path_value.append(elev)

print(sum(Path_value))