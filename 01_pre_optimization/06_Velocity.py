import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'

# web read DEM data
slope = wbe.read_raster('DEM_demo_slope.tif')
flow_accum = wbe.read_raster('DEM_demo_d8.tif')
velocity = wbe.new_raster(slope.configs)

for row in range(slope.configs.rows):
    for col in range(slope.configs.columns):
            velocity[row, col] = (flow_accum[row, col] ** 0.4 * slope[row, col] ** 0.3)/(5 ** 0.4 * 0.03 ** 0.6)

wbe.write_raster(velocity, 'DEM_demo_velocity.tif', compress=True)



# visualization
path_04 = '../00_data_source/DEM_demo_velocity.tif'
data_04 = rs.open(path_04)

fig, ax = plt.subplots(figsize=(8, 8))
show(data_04, cmap='Blues', title='DEM_demo_velocity', ax=ax)

plt.ticklabel_format(style='plain')
# ax.get_xaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# ax.get_yaxis().get_major_formatter().set_scientific(False)  # 关闭科学计数法
# grid and show plot
ax.grid(True,  linestyle='--', color='grey')
plt.show()


# value
Velocity_value = []
for row in range(velocity.configs.rows):
    for col in range(velocity.configs.columns):
        elev = velocity[row, col]
        Velocity_value.append(elev)

print(Velocity_value)
print(max(Velocity_value))
print(min(Velocity_value))