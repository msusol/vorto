"""Find a random seed that generates the lowest cost with brute force approach."""

import argparse
import evaluateShared as ev

from vrp import Solver

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputPath", help="Path to file containing problem", required=True)
    args=parser.parse_args()

    results = {}
    for i in range(200):
        vrp = Solver(args.inputPath)
        vrp.get_brute_force_routes(seed=i)
        schedules = vrp.get_schedules()
        cost = ev.getSolutionCost(vrp.problem, schedules)
        results[i] = cost[0]

    seeds = list({key:val for key,val in results.items() if val == min(results.values())}.keys())

    vrp = Solver(args.inputPath)
    vrp.get_brute_force_routes(seed=seeds[0])
    schedules = vrp.get_schedules()
    print('Cost:', ev.getSolutionCost(vrp.problem, schedules)[0])
    vrp.print_routes()