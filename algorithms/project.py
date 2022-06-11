from turtle import distance
import numpy as np
from math import dist
import math
import os
import sys


def sample(curr_location, attractions, visited, curr_time):
    
    # Distance to get from current location to attraction i
    distance = [dist((curr_location[0], curr_location[1]),(i[0], i[1])) for i in attractions]

    # Assign weights for each attractions:
    #   - if already visited, p = 0
    #   - if you can't visit & return within the remaining_time, p = 0
    #   - if not open, p = 0
    #   - else assign weight
    prob = []
    for i in range(len(attractions)):
        if (i+1) in visited:
            prob.append(0)
            continue
        
        waiting_time = 0
        if attractions[i][2] > (curr_time + distance[i]):
            waiting_time = attractions[i][2] - (curr_time + distance[i])

        t = attractions[i][5] + (distance[i] + dist((200,200),(attractions[i][0],attractions[i][1])))
        if t > 1440 - (curr_time + waiting_time):
            prob.append(0)
            continue
        
        if attractions[i][3] < curr_time + distance[i]:
            prob.append(0)
            continue

        # Otherwise, Assign weight/probability for sampling
        
        ratio = (attractions[i][4])/(attractions[i][5] + distance[i] + waiting_time + 0.0001)
        weight = ratio
        prob.append(weight)

    if sum(prob) == 0:
        return []

    # Normalize probability to sum to 1
    prob_norm = [(i/sum(prob)) for i in prob]

    n = int(len(attractions)/12)  #number of samples
    a = list(range(0, len(attractions)))
    samples = (np.random.choice(a, n, replace=True, p = prob_norm))

    return samples

# Among the samples, select the attraction with the highest ratio
# ratio = utility/time
def next_attraction(samples, attractions, curr_location):
    max = 0
    next = -1

    for i in samples:
        time = dist((attractions[i][0], attractions[i][1]), (curr_location[0],curr_location[1])) + attractions[i][5]
        ratio = attractions[i][4]/(time+0.00001)

        if ratio > max:
            max = ratio
            next = i
    
    return next


def explore(N, attractions):
    curr_location = [200,200]
    visited = []
    curr_time = 0

    while curr_time < 24*60:
        samples = sample(curr_location, attractions, visited, curr_time)
        next = next_attraction(samples, attractions, curr_location)

        # next == -1 means not enough time to visit anymore attractions
        if next == -1 or len(samples)==0:
            break
        
        if attractions[next][2] > curr_time + dist(curr_location, (attractions[next][0], attractions[next][1])):
            curr_time = attractions[next][2] + attractions[next][5]
        else:
            if (curr_time + dist(curr_location, (attractions[next][0], attractions[next][1]))) > attractions[next][3]:
                continue
            curr_time += (attractions[next][5] + dist(curr_location, (attractions[next][0], attractions[next][1])))
        
        if curr_time + dist((attractions[next][0], attractions[next][1]),(200,200)) > 1440:
            break
        else:
            visited.append(next+1)
            
        curr_location = [attractions[next][0], attractions[next][1]]
    
    utility = 0
    for i in visited:
        utility+=attractions[i-1][4]

    return visited, utility
    # All three parameters need to be updated as we visit different attractions
    ...
def best_solution(N, attractions):
    max = 0
    n = 80
    sequence =[]
    for i in range(n):
        visited, utility = explore(N, attractions)

        if utility > max:
            max = utility
            sequence = visited

    return sequence #, max

def read_input():
    N = int(input())
    attractions = [[int(i) for i in input().split()] for _ in range(N)]
    return N, attractions

def main():
    N, attractions = read_input()
    output = best_solution(N, attractions)
    print(len(output))
    print(*output)
    #print(max)

def solve_input(f, name):
    n = int(f.readline())
    rides = np.array([[int(i) for i in line.split()] for line in f])
    path = best_solution(n, rides)
    path = [str(x) for x in path]
    f = open("outputs/" + name[:-3] + ".out", "w")
    f.write(str(len(path)) + "\n")
    f.write(' '.join(path))


if __name__ == '__main__':
    main()
    # args = sys.argv[1]
    # if args[-3:] == ".in":
    #     # USAGE: py main.py admin_small1.in
    #     solve_input(open(args))
    # else:
    #     # USAGE: py main.py all_inputs
    #     d = os.fsencode(args)
    #     for file in os.listdir(d):
    #         filename = os.fsdecode(file)
    #         solve_input(open("all_inputs/" + filename), filename)

