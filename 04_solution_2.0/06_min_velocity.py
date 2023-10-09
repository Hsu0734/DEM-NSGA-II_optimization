import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\04_solution_2.0'

# web read DEM data
min_earth_volume = wbe.read_raster('min_earth_volume_dem.tif')
flow_accum_01 = wbe.d8_flow_accum(min_earth_volume, out_type="cells")
slope_01 = wbe.slope(min_earth_volume, units="percent")
velocity_01 = wbe.new_raster(flow_accum_01.configs)

min_flow_length = wbe.read_raster('min_flow_length_dem.tif')
flow_accum_02 = wbe.d8_flow_accum(min_flow_length, out_type="cells")
slope_02 = wbe.slope(min_flow_length, units='percent')
velocity_02 = wbe.new_raster(flow_accum_02.configs)

min_velocity = wbe.read_raster('min_velocity_dem.tif')
flow_accum_03 = wbe.d8_flow_accum(min_velocity, out_type="cells")
slope_03 = wbe.slope(min_velocity, units='percent')
velocity_03 = wbe.new_raster(flow_accum_03.configs)

balance = wbe.read_raster('balance_dem.tif')
flow_accum_04 = wbe.d8_flow_accum(balance, out_type="cells")
slope_04 = wbe.slope(balance, units='percent')
velocity_04 = wbe.new_raster(flow_accum_04.configs)


# path length
for row in range(flow_accum_01.configs.rows):
    for col in range(flow_accum_01.configs.columns):
        elev_01 = flow_accum_01[row, col]
        elev_02 = flow_accum_02[row, col]
        elev_03 = flow_accum_03[row, col]
        elev_04 = flow_accum_04[row, col]

        if elev_01 == flow_accum_01.configs.nodata:
            velocity_01[row, col] = flow_accum_01.configs.nodata
        elif elev_01 != flow_accum_01.configs.nodata:
            slope_factor_01 = (slope_01[row, col] / 100) ** 0.5
            flow_factor_01 = (flow_accum_01[row, col] * 100 * 0.000004215717) ** (2 / 3)
            velocity_01[row, col] = (slope_factor_01 * flow_factor_01 / 0.03) ** 0.6

        if elev_02 == flow_accum_02.configs.nodata:
            velocity_02[row, col] = flow_accum_02.configs.nodata
        elif elev_02 != flow_accum_02.configs.nodata:
            slope_factor_02 = (slope_02[row, col] / 100) ** 0.5
            flow_factor_02 = (flow_accum_02[row, col] * 100 * 0.000004215717) ** (2 / 3)
            velocity_02[row, col] = (slope_factor_02 * flow_factor_02 / 0.03) ** 0.6

        if elev_03 == flow_accum_03.configs.nodata:
            velocity_03[row, col] = flow_accum_03.configs.nodata
        elif elev_03 != flow_accum_03.configs.nodata:
            slope_factor_03 = (slope_03[row, col] / 100) ** 0.5
            flow_factor_03 = (flow_accum_03[row, col] * 100 * 0.000004215717) ** (2 / 3)
            velocity_03[row, col] = (slope_factor_03 * flow_factor_03 / 0.03) ** 0.6

        if elev_04 == flow_accum_04.configs.nodata:
            velocity_04[row, col] = flow_accum_04.configs.nodata
        elif elev_04 != flow_accum_04.configs.nodata:
            slope_factor_04 = (slope_04[row, col] / 100) ** 0.5
            flow_factor_04 = (flow_accum_04[row, col] * 100 * 0.000004215717) ** (2 / 3)
            velocity_04[row, col] = (slope_factor_04 * flow_factor_04 / 0.03) ** 0.6



wbe.write_raster(velocity_01, 'min_earth_volume_velocity.tif', compress=True)
wbe.write_raster(velocity_02, 'min_flow_length_velocity.tif', compress=True)
wbe.write_raster(velocity_03, 'min_velocity_velocity.tif', compress=True)
wbe.write_raster(velocity_04, 'balance_velocity.tif', compress=True)


# visualization
path_01 = '../04_solution_2.0/min_earth_volume_velocity.tif'
data_01 = rs.open(path_01)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_01, cmap='Blues', title='min_earth_volume_velocity', ax=ax, vmax=1.3)

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=20)
plt.ticklabel_format(style='plain')
ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
#ax.grid(True,  linestyle='--', color='grey')
plt.show()

# value
Path_value_01 = []
for row in range(velocity_01.configs.rows):
    for col in range(velocity_01.configs.columns):
        elev = velocity_01[row, col]
        if elev != velocity_01.configs.nodata:
            Path_value_01.append(elev)
print(max(Path_value_01))



path_02 = '../04_solution_2.0/min_flow_length_velocity.tif'
data_02 = rs.open(path_02)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_02, cmap='Blues', title='min_flow_length_velocity', ax=ax, vmax=1.3)

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=20)
plt.ticklabel_format(style='plain')
ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
#ax.grid(True,  linestyle='--', color='grey')
plt.show()

# value
Path_value_02 = []
for row in range(velocity_02.configs.rows):
    for col in range(velocity_02.configs.columns):
        elev = velocity_02[row, col]
        if elev != velocity_02.configs.nodata:
            Path_value_02.append(elev)
print(max(Path_value_02))



path_03 = '../04_solution_2.0/min_velocity_velocity.tif'
data_03 = rs.open(path_03)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_03, cmap='Blues', title='min_velocity_velocity', ax=ax, vmax=1.3)

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=20)
plt.ticklabel_format(style='plain')
ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
#ax.grid(True,  linestyle='--', color='grey')
plt.show()

# value
Path_value_03 = []
for row in range(velocity_03.configs.rows):
    for col in range(velocity_03.configs.columns):
        elev = velocity_03[row, col]
        if elev != velocity_03.configs.nodata:
            Path_value_03.append(elev)
print(max(Path_value_03))


path_04 = '../04_solution_2.0/balance_velocity.tif'
data_04 = rs.open(path_04)

fig, ax = plt.subplots(figsize=(16, 16))
ax.tick_params(axis='both', which='major', labelsize=20)
show(data_04, cmap='Blues', title='balance_velocity', ax=ax, vmax=1.3)

# Add colorbar
cbar_ax = fig.add_axes([0.92, 0.19, 0.03, 0.3])  # 调整颜色条的位置和大小
cbar = plt.colorbar(ax.images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=20)
plt.ticklabel_format(style='plain')
ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
#ax.grid(True,  linestyle='--', color='grey')
plt.show()

# value
Path_value_04 = []
for row in range(velocity_04.configs.rows):
    for col in range(velocity_04.configs.columns):
        elev = velocity_04[row, col]
        if elev != velocity_04.configs.nodata:
            Path_value_04.append(elev)
print(max(Path_value_04))