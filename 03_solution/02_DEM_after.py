import rasterio as rs
import matplotlib.pyplot as plt

# 定义DEM文件路径列表
dem_files = []

for i in range(10):
    filename = f'DEM_after_{10 * i}.tif'
    dem_files.append(filename)


# 创建一个子图网格
fig, axes = plt.subplots(nrows=2, ncols=5, figsize=(12, 6))

# 遍历DEM文件
for i, dem_file in enumerate(dem_files):
    # 打开DEM文件
    data_dem = rs.open(dem_file)

    # 在子图中显示DEM图像
    row = i // 5  # 行索引
    col = i % 5  # 列索引

    axes[row, col].imshow(data_dem.read(1), cmap='winter')
    axes[row, col].set_title(dem_file)
    axes[row, col].axis('off')

# 显示图形
plt.tight_layout()
plt.show()