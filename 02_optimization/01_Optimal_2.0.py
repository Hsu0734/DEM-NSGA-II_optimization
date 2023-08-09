'''
Multi-objective optimization: terrain optimal module
Author: Hanwen Xu
Version: 1
Date: Jul 29, 2023
'''

import whitebox_workflows as wbw
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas as pd


wbe = wbw.WbEnvironment()
wbe.verbose = False

wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
dem = wbe.read_raster('DEM_demo_resample.tif')

# creat a blank raster image of same size as the dem
cut_and_fill = wbe.new_raster(dem.configs)
# number of valid grid
n_grid = 0

for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        if dem[row, col] == dem.configs.nodata:
            cut_and_fill[row, col] = dem.configs.nodata
        elif dem[row, col] != dem.configs.nodata:
            cut_and_fill[row, col] = 0.0
            n_grid = n_grid + 1

# ------------------------------------------ #
# define MOO problem
class MyProblem(ElementwiseProblem):

    def __init__(self, n_grid, **kwargs):
        super().__init__(n_var=int(n_grid),
                         n_obj=3,
                         n_ieq_constr=1,
                         xl=np.array([0] * n_grid),
                         xu=np.array([2] * n_grid),
                         **kwargs)
        self.n_grid = n_grid

    def _evaluate(self, x, out, *args, **kwargs):

        var_list = []
        for i in range(n_grid):
            var_list.append(x[i])

        # notice your function should be Min function
        earth_volume_function = abs(sum(var_list)) * 100 * 5
        # earth_volume_function = abs(sum(var_list)) * 100 * 5 + sum(abs(i) for i in var_list) * 100 * 3 # grid resolution area: 100  unit price: 5
        flow_length_function = - path_sum_calculation(var_list)
        velocity_function = velocity_calculation(var_list)

        # notice your funciotn shoube < 0
        g1 = sum(var_list) * 100 - 100000

        out["F"] = [earth_volume_function, flow_length_function, velocity_function]
        out["G"] = [g1]

def path_sum_calculation(var_list):
    i = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            if dem[row, col] == dem.configs.nodata:
                cut_and_fill[row, col] = dem.configs.nodata
            elif dem[row, col] != dem.configs.nodata:
                cut_and_fill[row, col] = var_list[i]
                i = i + 1

    # creat dem_pop
    dem_pop = dem - cut_and_fill
    dem_pop_dep = wbe.breach_depressions_least_cost(dem_pop)

    # path length calculation
    flow_accum = wbe.d8_flow_accum(dem_pop_dep, out_type="sca")
    path_length = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col] # Read a cell value from a Raster
            if elev >= 83 and elev != flow_accum.configs.nodata:
                path_length[row, col] = 1.0
            elif elev < 83 or elev == flow_accum.configs.nodata:
                path_length[row, col] = 0.0

    path = []
    for row in range(path_length.configs.rows):
        for col in range(path_length.configs.columns):
            path.append(path_length[row, col])

    path_sum = sum(path)
    return path_sum


def velocity_calculation(var_list):
    i = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            if dem[row, col] == dem.configs.nodata:
                cut_and_fill[row, col] = dem.configs.nodata
            elif dem[row, col] != dem.configs.nodata:
                cut_and_fill[row, col] = var_list[i]
                i = i + 1

    # creat dem_pop_02
    dem_pop_02 = dem - cut_and_fill
    dem_pop_02_dep = wbe.breach_depressions_least_cost(dem_pop_02)

    # path length calculation
    flow_accum_02 = wbe.d8_flow_accum(dem_pop_02_dep, out_type="sca")
    slope = wbe.slope(dem_pop_02)

    velocity = wbe.new_raster(dem_pop_02.configs)

    for row in range(slope.configs.rows):
        for col in range(slope.configs.columns):
            velo = flow_accum_02[row, col]

            if velo == flow_accum_02.configs.nodata:
                velocity[row, col] = 0.0
            elif velo != flow_accum_02.configs.nodata:
                velocity[row, col] = ((flow_accum_02[row, col] * 0.01) ** 0.4 * slope[row, col] ** 0.3) / (
                            5 ** 0.4 * 0.03 ** 0.6)


    Velocity_value = []
    for row in range(velocity.configs.rows):
        for col in range(velocity.configs.columns):
            Velocity_value.append(velocity[row, col])

    max_velocity = max(Velocity_value)
    return max_velocity


problem = MyProblem(n_grid)


# choose algorithm
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination

algorithm = NSGA2(
    pop_size=100,
    n_offsprings=50,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)


termination = get_termination("n_gen", 300)

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

# 3D Visuliaztion
plot = Scatter(tight_layout=True)
plot.add(F, s=10)
plot.show()

# 2D Pairwise Scatter Plots
plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
plt.title("Flow path length (y) and total cost (x)")
plt.grid
plt.show()

plt.scatter(F[:, 1], F[:, 2], s=30, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and flow path length (x)")
plt.grid
plt.show()

plt.scatter(F[:, 0], F[:, 2], s=30, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and total cost (x)")
plt.grid
plt.show()


### Decision making ###
'''from pymoo.decomposition.asf import ASF

weights = np.array([0.5, 0.5])
approx_ideal = F.min(axis=0)
approx_nadir = F.max(axis=0)
nF = (F - approx_ideal) / (approx_nadir - approx_ideal)
decomp = ASF()
i = decomp.do(nF, 1/weights).argmin()
print("Best regarding ASF: Point \ni = %s\nF = %s" % (i, F[i]))

plt.figure(figsize=(7, 5))
plt.scatter(F, s=30, facecolors='none', edgecolors='blue')
plt.scatter(F[i, 0], F[i, 1], marker="x", color="red", s=200)
plt.title("Objective Space")
plt.grid
plt.show()'''


# save the data
result_df = pd.DataFrame(F)
result_df.to_csv('output.csv', index=False)


# visualization of solution set
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\03_solution'
for i in range(10):
    solution = res.X[10 * i] # 每隔十个取一个解
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
    filename = f'DEM_after_{10 * i}.tif'    #地形改动之后的结果
    wbe.write_raster(after_dem, file_name=filename, compress=True)

    filename_X = f'DEM_solution_{10 * i}.tif'   #地形自身的改动量
    wbe.write_raster(solution_dem, file_name=filename_X, compress=True)