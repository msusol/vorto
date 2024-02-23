# Vorto Algorithmic Challenge

For this challenge, you will submit a program that solves a version of the **Vehicle Routing
Problem (VRP)**.

The VRP specifies a set of loads to be completed efficiently by an unbounded number of
drivers.

Each load has a pickup location and a dropoff location, each specified by a Cartesian point. A
driver completes a load by driving to the pickup location, picking up the load, driving to the
dropoff, and dropping off the load. The time required to drive from one point to another, in
minutes, is the Euclidean distance between them. That is, to drive from (x1, y1) to (x2,
y2) takes `sqrt((x2-x1)^2 + (y2-y1)^2)` minutes.

As an example, suppose a driver located at (0,0) starts a load that picks up at (50,50) and
delivers at (100,100). This would take `2*sqrt(2*50^2) = ~141.42 minutes` of drive time
to complete: `sqrt((50-0)^2 + (50-0)^2)` minutes to drive to the pickup, and
`sqrt((100-50)^2 + (100-50)^2)` minutes to the dropoff.

Each driver starts and ends his shift at a depot located at (0,0). A driver may complete
multiple loads on his shift, but may not exceed 12 hours of total drive time. That is, the total
Euclidean distance of completing all his loads, including the return to (0,0), must be less than
12*60.

A VRP solution contains a list of drivers, each of which has an ordered list of loads to be
completed. All loads must be assigned to a driver.

The total cost of a solution is given by the formula:

```python
total_cost = 500*number_of_drivers + total_number_of_driven_minutes
```

A good program will produce a solution with a low total cost, but does not take too long to run
(see Evaluation section below).

**CVRPPD (Capacitated Vehicle Routing Problem with Pickup and Delivery)**

Interesting Read: [A Hybrid Genetic Algorithm for Solving the VRP with Pickup and Delivery
in Rural Areas](https://scholarspace.manoa.hawaii.edu/server/api/core/bitstreams/6e73b15f-13ae-489a-b8b9-3a4fcb9e57ba/content)

## Evaluate Training Problems

```bash
$ python3 evaluateShared.py --cmd "python3 vrp.py --inputPath" --problemDir "TrainingProblems"
```

| Approach                       | mean cost         | mean run time       |
|--------------------------------|-------------------|---------------------|
| get_brute_force_routes(seed=4) | 89750.38813192869 | 119.0253734588623ms |

### Demo

Taken from the challenge documentation, used for iterating on code directly.

given: `TestingProblems/demo.txt`

```
loadNumber pickup dropoff
1 (-50.1,80.0) (90.1,12.2)
2 (-24.5,-19.2) (98.5,1.8)
3 (0.3,8.9) (40.9,55.0)
4 (5.3,-61.1) (77.8,-5.4)
```

The minimum cost for the demo: `1856.364923582228`

```shell
$ python3 vrp.py --inputPath "TestingProblems/demo.txt"

[3, 1, 4]
[2]
```