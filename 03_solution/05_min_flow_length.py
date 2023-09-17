import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'

# web read DEM data
min_earth_volume = wbe.read_raster('min_earth_volume_dem.tif')
flow_accum_01 = wbe.d8_flow_accum(min_earth_volume, out_type="cells")
path_length_01 = wbe.new_raster(flow_accum_01.configs)

min_flow_length = wbe.read_raster('min_flow_length_dem.tif')
flow_accum_02 = wbe.d8_flow_accum(min_flow_length, out_type="cells")
path_length_02 = wbe.new_raster(flow_accum_02.configs)

min_velocity = wbe.read_raster('min_velocity_dem.tif')
flow_accum_03 = wbe.d8_flow_accum(min_velocity, out_type="cells")
path_length_03 = wbe.new_raster(flow_accum_03.configs)

# path length
for row in range(flow_accum_01.configs.rows):
    for col in range(flow_accum_01.configs.columns):
        elev_01 = flow_accum_01[row, col]
        elev_02 = flow_accum_02[row, col]
        elev_03 = flow_accum_03[row, col] # Read a cell value from a Raster

        if elev_01 >= 14.36 and elev_01 != flow_accum_01.configs.nodata:
            path_length_01[row, col] = 1.0 # Write the cell value of a Raster

        elif elev_01 < 14.36 and elev_01 != flow_accum_01.configs.nodata:
            path_length_01[row, col] = 0.0

        elif elev_01 == flow_accum_01.configs.nodata:
            path_length_01[row, col] = flow_accum_01.configs.nodata

        if elev_02 >= 14.36 and elev_02 != flow_accum_02.configs.nodata:
            path_length_02[row, col] = 1.0 # Write the cell value of a Raster

        elif elev_02 < 14.36 and elev_02 != flow_accum_02.configs.nodata:
            path_length_02[row, col] = 0.0

        elif elev_02 == flow_accum_02.configs.nodata:
            path_length_02[row, col] = flow_accum_02.configs.nodata

        if elev_03 >= 14.36 and elev_03 != flow_accum_03.configs.nodata:
            path_length_03[row, col] = 1.0 # Write the cell value of a Raster

        elif elev_03 < 14.36 and elev_03 != flow_accum_03.configs.nodata:
            path_length_03[row, col] = 0.0

        elif elev_03 == flow_accum_03.configs.nodata:
            path_length_03[row, col] = flow_accum_03.configs.nodata

wbe.write_raster(path_length_01, 'min_earth_volume_path.tif', compress=True)
wbe.write_raster(path_length_02, 'min_flow_length_path.tif', compress=True)
wbe.write_raster(path_length_03, 'min_velocity_path.tif', compress=True)


# visualization
path_01 = '../00_data_source/min_earth_volume_path.tif'
data_01 = rs.open(path_01)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_01, title='DEM_demo_path', ax=ax)

plt.ticklabel_format(style='plain')
ax.grid(True, linestyle='--', color='grey')
plt.show()

# value
Path_value_01 = []
for row in range(path_length_01.configs.rows):
    for col in range(path_length_01.configs.columns):
        elev = path_length_01[row, col]
        if elev != path_length_01.configs.nodata:
            Path_value_01.append(elev)
print(sum(Path_value_01))



path_02 = '../00_data_source/min_flow_length_path.tif'
data_02 = rs.open(path_02)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_02, title='DEM_demo_path', ax=ax)

plt.ticklabel_format(style='plain')
ax.grid(True, linestyle='--', color='grey')
plt.show()

# value
Path_value_02 = []
for row in range(path_length_02.configs.rows):
    for col in range(path_length_02.configs.columns):
        elev = path_length_02[row, col]
        if elev != path_length_02.configs.nodata:
            Path_value_02.append(elev)
print(sum(Path_value_02))



path_03 = '../00_data_source/min_velocity_path.tif'
data_03 = rs.open(path_03)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_03, title='DEM_demo_path', ax=ax)

plt.ticklabel_format(style='plain')
ax.grid(True, linestyle='--', color='grey')
plt.show()

# value
Path_value_03 = []
for row in range(path_length_03.configs.rows):
    for col in range(path_length_03.configs.columns):
        elev = path_length_03[row, col]
        if elev != path_length_03.configs.nodata:
            Path_value_03.append(elev)
print(sum(Path_value_03))
