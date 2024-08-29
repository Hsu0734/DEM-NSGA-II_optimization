import rasterio as rs
import matplotlib.pyplot as plt
from rasterio.plot import show

# 定义DEM文件路径列表
dem_files = []

for i in range(20):
    filename = f'DEM_after_{25 * i}.tif'
    dem_files.append(filename)


# 创建一个子图网格
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(72, 48))

# 遍历DEM文件
for i, dem_file in enumerate(dem_files):
    # 打开DEM文件
    data_dem = rs.open(dem_file)

    # 在子图中显示DEM图像
    row = i // 5  # 行索引
    col = i % 5  # 列索引

    show(data_dem, title=f'DEM_solution_{25 * i}', ax=axes[row, col])
    axes[row, col].set_title(dem_file)
    axes[row, col].axis('on')
    axes[row, col].ticklabel_format(style='plain')
    axes[row, col].grid(True, linestyle='--', color='grey')

# 显示图形
cbar_ax = fig.add_axes([0.9, 0.15, 0.02, 0.7])  # 调整colorbar位置和大小
cbar = plt.colorbar(axes[0, 0].images[0], cax=cbar_ax)
cbar.ax.tick_params(labelsize=12)
# plt.tight_layout()
plt.subplots_adjust(left=0.05, right=0.88, bottom=0.1, top=0.9,
                    wspace=0.4, hspace=0.1)
plt.suptitle("All DEM_after figure", fontsize=30)
plt.savefig("All DEM_after figure")
plt.show()