"""Assign the nearest load to optimize route loading."""

import argparse
import evaluateShared as ev

from vrp import Solver

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputPath", help="Path to file containing problem", required=True)
    args=parser.parse_args()

    vrp = Solver(args.inputPath)
    # TODO: Working through the algorithm for this approach.
    vrp.get_nearest_routes()
    schedules = vrp.get_schedules()
    print('Cost:', ev.getSolutionCost(vrp.problem, schedules)[0])
    vrp.print_routes()