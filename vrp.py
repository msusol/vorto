"""Vehicle Routing Problem (VRP) Solver."""

import argparse
import math
import numpy as np
import random
from collections import defaultdict
from typing import List

import evaluateShared as ev

class Solver():
    TIME_CONSTRAINT = 12*60
    DEPOT = ev.Point(0,0)

    def __init__(self, inputPath):
        self.inputPath = inputPath
        self.routes = defaultdict(list)
        self.problem = ev.loadProblemFromFile(inputPath)
        self.loadMatrix = self.calculate_load_matrix() # M
        self.depotDistOut = self.calculate_depot_distances(depot_out=True) # Dout
        self.depotDistBack = self.calculate_depot_distances(depot_out=False) # Dback

    def calculate_load_matrix(self):
        """Calculate a 'pseudo' distance matrix for loads."""
        # TODO: Can we do this greedily when reading file into problem?
        n = len(self.problem.loads)
        load_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                load_matrix[i, j] = ev.distanceBetweenPoints(self.problem.loads[i].dropoff, self.problem.loads[j].pickup)
        return load_matrix

    def calculate_depot_distances(self, depot_out=True):
        """Calculate the distance matrix for loads to/from depot."""
        n = len(self.problem.loads)
        dist_array = np.zeros(n)
        for i in range(n):
            if depot_out:
                dist_array[i] = ev.distanceBetweenPoints(self.DEPOT, self.problem.loads[i].pickup)
            else:
                dist_array[i] = ev.distanceBetweenPoints(self.problem.loads[i].dropoff, self.DEPOT)
        return dist_array

    def get_route_distance(self, schedule: List[ev.Load]) -> int:
        """Get full route distance of schedule.
        Ex: [1,3] load.id - 1 = matrix (M) offset
          distance = Dout[0] + M[0][0] + M[0][2] + M[2][2] + Dback[2]
        """
        assert len(schedule) > 0

        def matrix_offset(i):
            # Convert load.id: str -> int
            return int(schedule[i].id)-1

        # Depot out (Dout)
        distance = self.depotDistOut[matrix_offset(0)]
        for idx in range(len(schedule)):
            # Load Demand
            #print('M[%s][%s]'%(matrix_offset(idx), matrix_offset(idx)))
            distance += self.loadMatrix[matrix_offset(idx)][matrix_offset(idx)]
            # Previous load deadhead
            if idx != 0:
                #print('M[%s][%s]'%(matrix_offset(idx-1), matrix_offset(idx)))
                distance += self.loadMatrix[matrix_offset(idx-1)][matrix_offset(idx)]
        # Depot back (Dback)
        distance += self.depotDistBack[matrix_offset(idx)]

        return distance

    # Work In Progress
    def get_closest_load_id(self, M, load):
        """Closet load in load matrix, M, by load.id."""
        offset = load - 1
        min_distance = math.inf
        min_idx = None
        for idx, val in np.ndenumerate(M[offset]):
            if idx[0] != offset:
                if val < min_distance:
                    min_distance = val
                    min_idx = idx[0] + 1
        return min_idx

    def get_brute_force_routes(self, seed=42):
        driver = 1
        schedule = []
        random.seed(seed)
        random.shuffle(self.problem.loads)
        for load in self.problem.loads:
            schedule.append(load)
            distance = self.get_route_distance(schedule)
            if distance > self.TIME_CONSTRAINT:
                schedule = [load]
                driver += 1
            self.routes[driver].append(load)

    def get_schedules(self):
        schedules = []
        for route in self.routes.items():
            schedules.append([load.id for load in route[1]])
        return schedules

    def print_routes(self):
        for route in self.routes.items():
            print([int(load.id) for load in route[1]])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputPath", help="Path to file containing problem", required=True)
    args=parser.parse_args()

    vrp = Solver(args.inputPath)
    vrp.get_brute_force_routes(seed=4) # Only optimial for demo.txt
    # Print to stdout
    vrp.print_routes()