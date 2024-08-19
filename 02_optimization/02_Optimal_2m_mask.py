"""
Multi-objective optimization: Sink volume & retention volume & earthwork
Author: Hanwen Xu
Version: 1
Date: July 16, 2024
"""

import whitebox_workflows as wbw
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas as pd

wbe = wbw.WbEnvironment()
wbe.verbose = False

wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
mask = wbe.read_raster('Hanwen_2m_mask.tif')
dem = wbe.read_raster('Hanwen_2m.tif')

# creat a blank raster image of same size as the dem
layer = wbe.new_raster(mask.configs)

# number of valid grid
grid = []
q = 1
for row in range(mask.configs.rows):
    for col in range(mask.configs.columns):
        if dem[row, col] == mask.configs.nodata:
            layer[row, col] = mask.configs.nodata
        elif dem[row, col] != mask.configs.nodata and mask[row, col] == mask.configs.nodata:
            layer[row, col] = 0.0
        elif dem[row, col] != mask.configs.nodata:
            layer[row, col] = 0.0
            grid.append(q)
n_grid = sum(grid)
print(n_grid)


# ------------------------------------------ #
# define MOO problem
class MyProblem(ElementwiseProblem):

    def __init__(self, n_grid, **kwargs):
        super().__init__(n_var=int(n_grid),
                         n_obj=3,
                         n_ieq_constr=0,
                         n_eq_constr=0,
                         xl=np.array([-1] * n_grid),
                         xu=np.array([1] * n_grid),
                         **kwargs)
        self.n_grid = n_grid

    def _evaluate(self, x, out, *args, **kwargs):
        var_list = []
        for i in range(n_grid):
            var_list.append(x[i])

        # notice your function should be Min function
        earth_volume_function = sum(abs(i) for i in var_list) * 4 * 8 / 1000000
        flow_length_function, velocity_function = path_sum_calculation(var_list)

        out["F"] = [earth_volume_function, flow_length_function, velocity_function]

def path_sum_calculation(var_list):
    i = 0
    cut_and_fill = wbe.new_raster(dem.configs)
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            if dem[row, col] == dem.configs.nodata:
                cut_and_fill[row, col] = dem.configs.nodata
            elif dem[row, col] != dem.configs.nodata and mask[row, col] == mask.configs.nodata:
                cut_and_fill[row, col] = 0.0
            elif dem[row, col] != dem.configs.nodata and mask[row, col] != mask.configs.nodata:
                cut_and_fill[row, col] = var_list[i]
                i = i + 1

    dem_pop = dem - cut_and_fill

    # path length calculation
    flow_accum = wbe.d8_flow_accum(dem_pop, out_type='cells')
    path_length = wbe.new_raster(flow_accum.configs)

    slope = wbe.slope(dem_pop, units="percent")
    velocity = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col]  # Read a cell value from a Raster
            if elev >= 91.90 and elev != flow_accum.configs.nodata:
                path_length[row, col] = - 1.0
            elif elev < 91.90 or elev == flow_accum.configs.nodata:
                path_length[row, col] = 0.0

    path = []
    for row in range(path_length.configs.rows):
        for col in range(path_length.configs.columns):
            path.append(path_length[row, col])

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            velo = flow_accum[row, col]
            if velo == flow_accum.configs.nodata:
                velocity[row, col] = slope.configs.nodata
            elif velo != flow_accum.configs.nodata:
                slope_factor = (slope[row, col] / 100) ** 0.5
                flow_factor = (flow_accum[row, col] * 4 * 0.000004215717) ** (2 / 3)
                velocity[row, col] = (slope_factor * flow_factor / 0.03) ** 0.6

    velocity_value = []
    for row in range(velocity.configs.rows):
        for col in range(velocity.configs.columns):
            velocity_value.append(velocity[row, col])

    path_sum = sum(path)
    max_velocity = max(velocity_value)

    return path_sum, max_velocity

problem = MyProblem(n_grid)

# choose algorithm
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination

algorithm = NSGA2(
    pop_size=500,
    n_offsprings=200,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)


termination = get_termination("n_gen", 200)

from pymoo.optimize import minimize
res = minimize(problem,
               algorithm,
               termination,
               seed=1,
               save_history=True,
               verbose=True)

X = res.X
F = res.F


# Visualization of Objective space or Variable space
from pymoo.visualization.scatter import Scatter
import matplotlib.pyplot as plt

# 3D Visualization
plot = Scatter(tight_layout=True)
plot.add(F, s=10)
plot.show()

# 2D Pairwise Scatter Plots
plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=20, facecolors='none', edgecolors='blue')
plt.title("Flow path length (y) and total cost (x)")
plt.grid()
plt.show()

plt.scatter(F[:, 1], F[:, 2], s=20, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and flow path length (x)")
plt.grid()
plt.show()

plt.scatter(F[:, 0], F[:, 2], s=20, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and total cost (x)")
plt.grid()
plt.show()


# save the data
result_df = pd.DataFrame(F)
result_df.to_csv('output_2m.csv', index=False)
result_df = pd.DataFrame(X)
result_df.to_csv('output_variable_2m.csv', index=False)

### Decision making ###
### Min Decision ###
min_earth_volume = np.argmin(F[:, 0])
min_flow_length = np.argmin(F[:, 1])
min_velocity = np.argmin(F[:, 2])

min_earth_volume_solution = res.X[min_earth_volume]
min_flow_length_solution = res.X[min_flow_length]
min_velocity_solution = res.X[min_velocity]

min_earth_volume_dem = wbe.new_raster(dem.configs)
min_flow_length_dem = wbe.new_raster(dem.configs)
min_velocity_dem = wbe.new_raster(dem.configs)

wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'
t = 0
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        if dem[row, col] == dem.configs.nodata:
            min_earth_volume_dem[row, col] = dem.configs.nodata
            min_flow_length_dem[row, col] = dem.configs.nodata
            min_velocity_dem[row, col] = dem.configs.nodata

        elif dem[row, col] != dem.configs.nodata:
            min_earth_volume_dem[row, col] = min_earth_volume_solution[t]
            min_flow_length_dem[row, col] = min_flow_length_solution[t]
            min_velocity_dem[row, col] = min_velocity_solution[t]
            t = t + 1

wbe.write_raster(min_earth_volume_dem, file_name='min_earth_volume_solution', compress=True)
wbe.write_raster(min_flow_length_dem, file_name='min_flow_length_solution', compress=True)
wbe.write_raster(min_velocity_dem, file_name='min_velocity_solution', compress=True)

after_dem_minEV = dem - min_earth_volume_dem
after_dem_minFL = dem - min_flow_length_dem
after_dem_minV = dem - min_velocity_dem

wbe.write_raster(after_dem_minEV, file_name='min_earth_volume_dem', compress=True)
wbe.write_raster(after_dem_minFL, file_name='min_flow_length_dem', compress=True)
wbe.write_raster(after_dem_minV, file_name='min_velocity_dem', compress=True)

### balance Decision ###
from pymoo.decomposition.asf import ASF

weights = np.array([0.333, 0.333, 0.333])
approx_ideal = F.min(axis=0)
approx_nadir = F.max(axis=0)
nF = (F - approx_ideal) / (approx_nadir - approx_ideal)
decomp = ASF()
k = decomp.do(nF, 1/weights).argmin()
print("Best regarding ASF: Point \nk = %s\nF = %s" % (k, F[k]))

plot = Scatter(tight_layout=True)
plot.add(F, s=10)
plot.add(F[k], s=70, color="red")
plot.show()

balance_solution = res.X[k]
balance_dem = wbe.new_raster(dem.configs)
q = 0
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        if dem[row, col] == dem.configs.nodata:
            balance_dem[row, col] = dem.configs.nodata
        elif dem[row, col] != dem.configs.nodata:
            balance_dem[row, col] = balance_solution[q]
            q = q + 1

wbe.write_raster(balance_dem, file_name='min_balance_solution', compress=True)
after_dem_balance = dem - balance_dem
wbe.write_raster(after_dem_balance, file_name='min_balance_dem', compress=True)


# visualization of solution set
for i in range(20):
    solution = res.X[25 * i] # 每隔十个取一个解
    solution_dem = wbe.new_raster(dem.configs)

    p = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            if dem[row, col] == dem.configs.nodata:
                solution_dem[row, col] = dem.configs.nodata
            elif dem[row, col] != dem.configs.nodata:
                solution_dem[row, col] = solution[p]
                p = p + 1

    after_dem = dem - solution_dem
    filename = f'DEM_after_{25 * i}.tif'    #地形改动之后的结果
    wbe.write_raster(after_dem, file_name=filename, compress=True)

    filename_X = f'DEM_solution_{25 * i}.tif'   #地形自身的改动量
    wbe.write_raster(solution_dem, file_name=filename_X, compress=True)