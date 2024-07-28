'''
Multi-objective optimization: terrain optimal module
Author: Hanwen Xu
Version: 1
Date: Sep 06, 2023
only cut the DEM, the elevation can only be decreased
'''

import whitebox_workflows as wbw
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas as pd


wbe = wbw.WbEnvironment()
wbe.verbose = False

wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
dem = wbe.read_raster('Hanwen_10m.tif')

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
        earth_volume_function = abs(sum(var_list)) * 100 * 8 / 10000
        # earth_volume_function = abs(sum(var_list)) * 100 * 5 + sum(abs(i) for i in var_list) * 100 * 3 # grid resolution area: 100  unit price: 5
        flow_length_function = - path_sum_calculation(var_list)
        velocity_function = velocity_calculation(var_list)

        # notice your funciotn shoube < 0
        g1 = sum(var_list) * 100 - 300000
        g2 = 510 - path_sum_calculation(var_list)

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
    fill_dep = wbe.fill_depressions(dem_pop)
    flow_accum = wbe.d8_flow_accum(fill_dep, out_type='cells')
    path_length = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col] # Read a cell value from a Raster
            if elev >= 38.8 and elev != flow_accum.configs.nodata:
                path_length[row, col] = 1.0
            elif elev < 38.8 or elev == flow_accum.configs.nodata:
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
    fill_dep_02 = wbe.fill_depressions(dem_pop_02)
    flow_accum_02 = wbe.d8_flow_accum(fill_dep_02, out_type='cells')
    slope = wbe.slope(dem_pop_02, units="percent")

    velocity = wbe.new_raster(slope.configs)

    for row in range(slope.configs.rows):
        for col in range(slope.configs.columns):
            velo = slope[row, col]
            if velo == slope.configs.nodata:
                velocity[row, col] = slope.configs.nodata
            elif velo != slope.configs.nodata:
                velocity[row, col] = (((flow_accum_02[row, col] * 100 * 0.000005701259) ** 0.4) * (
                            (slope[row, col] / 100) ** 0.3)) / ((10 ** 0.4) * (0.03 ** 0.6))
                #slope_factor = (slope[row, col] / 100) ** 0.5
                #flow_factor = (flow_accum_02[row, col] * 100 * 0.000005701259) ** (2 / 3)
                #velocity[row, col] = (slope_factor * flow_factor / 0.03) ** 0.6


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

# 3D Visuliaztion
plot = Scatter(tight_layout=True)
plot.add(F, s=10)
plot.show()

# 2D Pairwise Scatter Plots
plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=20, facecolors='none', edgecolors='blue')
plt.title("Flow path length (y) and total cost (x)")
plt.grid
plt.show()

plt.scatter(F[:, 1], F[:, 2], s=20, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and flow path length (x)")
plt.grid
plt.show()

plt.scatter(F[:, 0], F[:, 2], s=20, facecolors='none', edgecolors='blue')
plt.title("Max velocity (y) and total cost (x)")
plt.grid
plt.show()