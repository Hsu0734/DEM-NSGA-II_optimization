import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt

# whitebox default setting
wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'

# Create a shared colorbar axis
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(72, 48))
cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.7])  # Adjust the position and size of the colorbar

# Initialize variables to store min and max velocity values for color scaling
vmin = float('inf')
vmax = float('-inf')

# Initialize a list to store the images for each subplot
images = []

# read image loop
for i in range(20):
    filename = f'DEM_after_{25 * i}.tif'
    dem = wbe.read_raster(file_name=filename)  # read the DEM

    flow_accum = wbe.d8_flow_accum(dem, out_type='cells')  # d8_analysis
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

                # Update vmin and vmax based on the current velocity value
                velo_value = velocity[row, col]
                if velo_value != velocity.configs.nodata:
                    vmin = min(vmin, velo_value)
                    vmax = max(vmax, velo_value)

    flow_filename = f'DEM_velocity_{25 * i}.tif'
    wbe.write_raster(velocity, file_name=flow_filename, compress=True)

    path = rf"DEM_velocity_{25 * i}.tif"
    data = rs.open(path)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    img = axes[row, col].imshow(data.read(1), cmap='Blues', vmin=vmin, vmax=1.5)  # 设置子图的颜色标度范围
    images.append(img)

    # axes[row, col].set_title(f'DEM_velocity_{10 * i}')
    # axes[row, col].axis('on')
    # axes[row, col].ticklabel_format(style='plain')
    # axes[row, col].grid(True, linestyle='--', color='black')

# Create a colorbar using the first image's colormap
cbar = plt.colorbar(images[0], cax=cbar_ax, orientation='vertical')
cbar.set_label('Velocity')  # 设置颜色条标签

plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM velocity figure", fontsize=30)
plt.savefig("All DEM velocity figure")
plt.show()
