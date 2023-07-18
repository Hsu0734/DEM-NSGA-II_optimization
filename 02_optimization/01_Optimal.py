'''
Multi-objective optimization: terrain optimal module
Author: Hanwen Xu
Version: 1
Date: Jul 17, 2023
'''

import whitebox_workflows as wbw
import rasterio as rs
from rasterio.plot import show, show_hist
from pymoo.core.problem import ElementwiseProblem
import numpy as np
import pandas as pd


wbe = wbw.WbEnvironment()
wbe.verbose = False
wbe.working_directory = r'D:\PhD career\05 SCI papers\05 Lundtoftegade AKB\Lundtoftegade_optimization\00_data_source'
dem = wbe.read_raster('Hanwen.tif')
n_grid = int(dem.configs.rows) * int(dem.configs.columns) # 栅格总数

# creat a blank raster image of same size as the dem
cut_and_fill = wbe.new_raster(dem.configs)
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        cut_and_fill[row, col] = 0.0


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
        earth_volume_function = sum(var_list) * 25 * 5  # grid resolution area: 25  unit price: 5
        flow_length_function = - path_sum_calculation(var_list)
        velocity_function = velocity_calculation(var_list)

        # notice your funciotn shoube < 0
        g1 = sum(var_list) - 500

        out["F"] = [earth_volume_function, flow_length_function, velocity_function]
        out["G"] = [g1]

def path_sum_calculation(var_list):
    i = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            cut_and_fill[row, col] = var_list[i]
            i = i + 1

    # creat dem_pop
    dem_pop = dem - cut_and_fill

    # path length calculation
    wbe = wbw.WbEnvironment()
    wbe.verbose = False
    flow_accum = wbe.d8_flow_accum(dem_pop, out_type="sca")
    path_length = wbe.new_raster(flow_accum.configs)

    for row in range(flow_accum.configs.rows):
        for col in range(flow_accum.configs.columns):
            elev = flow_accum[row, col] # Read a cell value from a Raster
            if elev >= 200.0 and elev != flow_accum.configs.nodata:
                path_length[row, col] = 1.0
            elif elev < 200.0 or elev == flow_accum.configs.nodata:
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
            cut_and_fill[row, col] = var_list[i]
            i = i + 1

    # creat dem_pop
    dem_pop = dem - cut_and_fill

    # path length calculation
    wbe = wbw.WbEnvironment()
    wbe.verbose = False
    flow_accum = wbe.d8_flow_accum(dem_pop, out_type="sca")
    slope = wbe.slope(dem_pop)

    velocity = wbe.new_raster(dem_pop.configs)

    for row in range(slope.configs.rows):
        for col in range(slope.configs.columns):
            velocity[row, col] = (flow_accum[row, col] ** 0.4 * slope[row, col] ** 0.3) / (5 ** 0.4 * 0.03 ** 0.6)


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


termination = get_termination("n_gen", 500)

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
import matplotlib.pyplot as plt
from pymoo.visualization.scatter import Scatter

# xl, xu = problem.bounds()
plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
plt.title("Objective Space")
plt.show()

# Decision making
from pymoo.decomposition.asf import ASF

weights = np.array([0.5, 0.5])
approx_ideal = F.min(axis=0)
approx_nadir = F.max(axis=0)
nF = (F - approx_ideal) / (approx_nadir - approx_ideal)
decomp = ASF()
i = decomp.do(nF, 1/weights).argmin()
print("Best regarding ASF: Point \ni = %s\nF = %s" % (i, F[i]))

plt.figure(figsize=(7, 5))
plt.scatter(F[:, 0], F[:, 1], s=30, facecolors='none', edgecolors='blue')
plt.scatter(F[i, 0], F[i, 1], marker="x", color="red", s=200)
plt.title("Objective Space")
plt.grid
plt.show()


# save the data
result_df = pd.DataFrame(F)
result_df.to_csv('output.csv', index=False)


# visualization of solution set
wbe.working_directory = r'D:\PhD career\05 SCI papers\06 Multi-objective optimization\MOO practices\Solution'
for i in range(10):
    solution = res.X[2 * i] # 每隔一个取一个解

    solution_dem = wbe.new_raster(dem.configs)
    p = 0
    for row in range(dem.configs.rows):
        for col in range(dem.configs.columns):
            solution_dem[row, col] = solution[p]
            after_dem = dem - solution_dem
            filename = f'DEM_solution_{i}.tif'
            wbe.write_raster(after_dem, file_name=filename, compress=True)
            p = p + 1
