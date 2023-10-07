"""
Multi-objective optimization: topographic modification optimization
Author: Hanwen Xu
Version: 1
Date: Sep 06, 2023
"""

import whitebox_workflows as wbw
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas as pd


wbe = wbw.WbEnvironment()
wbe.verbose = False

wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
dem = wbe.read_raster('DEM_demo_resample_10m.tif')

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
print(n_grid)

# ------------------------------------------ #
# define MOO problem
class MyProblem(ElementwiseProblem):

    def __init__(self, n_grid, **kwargs):
        super().__init__(n_var=int(n_grid),
                         n_obj=3,
                         n_ieq_constr=2,
                         xl=np.array([0] * n_grid),
                         xu=np.array([2] * n_grid),
                         **kwargs)
        self.n_grid = n_grid

    def _evaluate(self, x, out, *args, **kwargs):

        var_list = []
        for i in range(n_grid):
            var_list.append(x[i])

        # notice your function should be Min function
        earth_volume_function = abs(sum(var_list)) * 100 * 8 / 1000000
        # earth_volume_function = abs(sum(var_list)) * 100 * 8 + sum(abs(i) for i in var_list) * 100 * 4
        # resolution area: 100m^2  unit price: 5
        flow_length_function = - (path_sum_calculation(var_list))
        velocity_function = velocity_calculation(var_list)

        # notice your function should be <= 0
        g1 = sum(abs(i) for i in var_list) * 100 - 300000
        g2 = - (path_sum_calculation(var_list)) + 500

        out["F"] = [earth_volume_function, flow_length_function, velocity_function]
        out["G"] = [g1, g2]

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

    # path length calculation
    flow_accum = wbe.d8_flow_accum(dem_pop, out_type='cells')
    path_length = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col]   # Read a cell value from a Raster
            if elev >= 14.36 and elev != flow_accum.configs.nodata:
                path_length[row, col] = 1.0
            elif elev < 14.36 or elev == flow_accum.configs.nodata:
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

    # path length calculation
    flow_accum_02 = wbe.d8_flow_accum(dem_pop_02, out_type='cells')
    slope = wbe.slope(dem_pop_02, units="percent")

    velocity = wbe.new_raster(flow_accum_02.configs)

    for row in range(flow_accum_02.configs.rows):
        for col in range(flow_accum_02.configs.columns):
            velo = flow_accum_02[row, col]
            if velo == flow_accum_02.configs.nodata:
                velocity[row, col] = slope.configs.nodata
            elif velo != flow_accum_02.configs.nodata:
                slope_factor = (slope[row, col] / 100) ** 0.5
                flow_factor = (flow_accum_02[row, col] * 100 * 0.000004215717) ** (2 / 3)
                velocity[row, col] = (slope_factor * flow_factor / 0.03) ** 0.6

    velocity_value = []
    for row in range(velocity.configs.rows):
        for col in range(velocity.configs.columns):
            velocity_value.append(velocity[row, col])

    max_velocity = max(velocity_value)
    return max_velocity

problem = MyProblem(n_grid)


# choose algorithm
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.operators.crossover.sbx import SBX
from pymoo.operators.mutation.pm import PM
from pymoo.operators.sampling.rnd import FloatRandomSampling
from pymoo.termination import get_termination

algorithm = NSGA2(
    pop_size=200,
    n_offsprings=100,
    sampling=FloatRandomSampling(),
    crossover=SBX(prob=0.9, eta=15),
    mutation=PM(eta=20),
    eliminate_duplicates=True
)


termination = get_termination("n_gen", 300, additional=lambda algo, _=None: algo.n_gen == 100 or algo.n_gen == 200)

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



# 100和200代
generation100 = res.history[np.where(res.history["n_gen"] == 100)]
generation200 = res.history[np.where(res.history["n_gen"] == 200)]

F_100 = generation100["F"]
plot = Scatter(tight_layout=True)
plot.add(F_100, s=10)
plot.show()

plt.figure(figsize=(7, 5))
plt.scatter(F_100[:, 0], F_100[:, 1], s=20, facecolors='none', edgecolors='red')
plt.title("Flow path length (y) and total cost (x)")
plt.grid()
plt.show()

plt.scatter(F_100[:, 1], F_100[:, 2], s=20, facecolors='none', edgecolors='red')
plt.title("Max velocity (y) and flow path length (x)")
plt.grid()
plt.show()

plt.scatter(F_100[:, 0], F_100[:, 2], s=20, facecolors='none', edgecolors='red')
plt.title("Max velocity (y) and total cost (x)")
plt.grid()
plt.show()

# 可视化200代的结果
F_200 = generation200["F"]
plot = Scatter(tight_layout=True)
plot.add(F_200, s=10)
plot.show()

plt.figure(figsize=(7, 5))
plt.scatter(F_200[:, 0], F_200[:, 1], s=20, facecolors='none', edgecolors='green')
plt.title("Flow path length (y) and total cost (x)")
plt.grid()
plt.show()

plt.scatter(F_200[:, 1], F_200[:, 2], s=20, facecolors='none', edgecolors='green')
plt.title("Max velocity (y) and flow path length (x)")
plt.grid()
plt.show()

plt.scatter(F_200[:, 0], F_200[:, 2], s=20, facecolors='none', edgecolors='green')
plt.title("Max velocity (y) and total cost (x)")
plt.grid()
plt.show()


