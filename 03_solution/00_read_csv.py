import pandas as pd
import rasterio as rs
from rasterio.plot import show
import matplotlib.pyplot as plt
import whitebox_workflows as wbw

# 读取CSV文件
df = pd.read_csv('output_variable_10m.csv')

wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
dem = wbe.read_raster('Hanwen_10m.tif')

# 循环处理CSV文件中的0到99行
for n in range(50):

    row = df.iloc[int(n)]
    row_list = row.tolist()

    layer = wbe.new_raster(dem.configs)
    m = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            if dem[row, col] == dem.configs.nodata:
                layer[row, col] = dem.configs.nodata
            elif dem[row, col] != dem.configs.nodata and dem[row, col] == dem.configs.nodata:
                layer[row, col] = 0.0
            elif dem[row, col] != dem.configs.nodata:
                layer[row, col] = row_list[m]
                m += 1

    #dem_solution = dem5m - layer
    dem_solution = wbe.raster_calculator(expression="'dem' - 'layer'", input_rasters=[dem, layer])

    flow_accum = wbe.d8_flow_accum(dem_solution, out_type='cells')
    path_length = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col]  # Read a cell value from a Raster
            if elev >= 14.36 and elev != flow_accum.configs.nodata:
                path_length[row, col] = 1.0
            elif elev < 14.36 or elev == flow_accum.configs.nodata:
                path_length[row, col] = 0.0

    wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'
    output_filename = f'DEM10m_path_length_{n}.tif'
    wbe.write_raster(path_length, output_filename, compress=True)

    # visualization
    path_01 = f'../03_solution/{output_filename}'
    data_01 = rs.open(path_01)

    fig, ax = plt.subplots(figsize=(16, 16))
    ax.tick_params(axis='both', which='major', labelsize=20)
    show(data_01, title=f'DEM_sink_{n}', ax=ax)
    plt.ticklabel_format(style='plain')
    plt.show()
    plt.close(fig)  # 关闭图形以释放内存