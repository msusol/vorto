"""Vehicle Routing Problem (VRP) Solver."""

import argparse
import math
import numpy as np
import random
import sys
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
        self.loads_to_schedule = None
        self.distance_depot_out = None
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

        # Is the nearest_idx in the loads to schedule list.
    def has_load_to_schedule(self, nearest_idx):
        nearest_id = nearest_idx + 1
        return nearest_id in [int(load.id) for load in self.loads_to_schedule]

    def get_closest_load(self, load_id: str):
        """Closet load in load matrix, M, by load.id."""
        matrix_offset = int(load_id) - 1
        min_distance = math.inf
        min_idx = None
        for idx, val in enumerate(self.loadMatrix[matrix_offset]):
            if idx != matrix_offset and self.has_load_to_schedule(idx):
                if val < min_distance:
                    min_distance = val
                    min_idx = idx + 1
        try:
            return [load for load in self.loads_to_schedule if int(load.id) == min_idx][0]
        except:
            print('TODO: Resolve this issue on real training data.')
            sys.exit(1)

    def remove_depot_out(self, load_id: str):
        return [t for t in self.distance_depot_out if t[0] != int(load_id)]

    def get_load(self, load_id: str):
        return [load for load in self.loads_to_schedule if load.id == load_id][0]

    def remove_load(self, load_id: str):
        return [load for load in self.loads_to_schedule if load.id != load_id]

    def get_nearest_routes(self):
        self.loads_to_schedule = self.problem.loads.copy() # List[ev.Load]
        # Maintain load.id: k+1
        self.distance_depot_out = [(k+1,v) for k, v in enumerate(self.depotDistOut)]

        self.routes = {}

        # Start with the closest load to the depot, assign to driver #1, remove from loads to schedule.
        driver = 1
        closest_load = min(self.distance_depot_out, key = lambda t: t[1])  # TODO: Tuple
        closest_load_id = str(closest_load[0])
        #self.routes[driver].append(self.loads_to_schedule[closest_load[0]])  # TODO: Make this a Load object
        new_load = self.get_load(closest_load_id)

        self.routes[driver] = []

        self.routes[driver].append(new_load)  # TODO: Make this a Load object
        self.distance_depot_out = self.remove_depot_out(new_load.id)
        self.loads_to_schedule = self.remove_load(new_load.id)

        while len(self.loads_to_schedule):
            # Now let's cycle through the driver routes and attempt to append the closest load
            # to the route, otherwise we find the next closest to depot and start with new driver.
            for driver, route in self.routes.copy().items(): # RuntimeError: dictionary changed size during iteration
                # Get the closest load to route's last load drop off point.
                last_load = route[-1]
                nearest_load = self.get_closest_load(last_load.id)
                # Get the round trip distance now with an additional load in route.
                distance = self.get_route_distance(route + [nearest_load])
                if distance > self.TIME_CONSTRAINT:
                    # Find the next closest point from depot to start a new driver route.
                    driver += 1
                    closest_load = min(self.distance_depot_out, key = lambda t: t[1])
                    closest_load_id = str(closest_load[0])
                    new_load = self.get_load(closest_load_id)
                    self.routes[driver] = []
                    self.routes[driver].append(new_load)
                    self.loads_to_schedule = self.remove_load(new_load.id)
                    self.distance_depot_out = self.remove_depot_out(new_load.id)
                else:
                    new_load = self.get_load(nearest_load.id)
                    self.routes[driver].append(new_load)
                    self.loads_to_schedule = self.remove_load(new_load.id)
                    self.distance_depot_out = self.remove_depot_out(new_load.id)

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
    vrp.get_nearest_routes()
    # Print to stdout
    vrp.print_routes()