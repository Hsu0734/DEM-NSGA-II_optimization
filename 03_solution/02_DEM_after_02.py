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

# 遍历DEM文件
for i in range(20):
    filename = f'DEM_after_{10 * i}.tif'
    dem = wbe.read_raster(file_name=filename)

    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            elev_value = dem[row, col]
            if elev_value != dem.configs.nodata:
                vmin = min(vmin, elev_value)
                vmax = max(vmax, elev_value)

    path = rf"DEM_after_{10 * i}.tif"
    data = rs.open(path)

    row = i // 5  # 行索引
    col = i % 5  # 列索引

    img = axes[row, col].imshow(data.read(1), vmin=vmin, vmax=vmax)  # 设置子图的颜色标度范围
    images.append(img)

    #axes[row, col].set_title(f'DEM_after_{10 * i}')
    #axes[row, col].axis('on')
    #axes[row, col].ticklabel_format(style='plain')
    #axes[row, col].grid(True, linestyle='--', color='black')

# Create a colorbar using the first image's colormap
cbar = plt.colorbar(images[0], cax=cbar_ax, orientation='vertical')
cbar.set_label('Velocity')  # 设置颜色条标签

plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM_after figure", fontsize=30)
plt.savefig("All DEM_after figure")
plt.show()