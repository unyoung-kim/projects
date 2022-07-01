# NP Complete problem
The goal of this project is to suggest an optimal solution to the 

## Inputs
### The program takes in the following inputs
- N: The number of nodes
- N lines for each node 
  - xi, yi: the coordinate of a nodem, Ai, in the grph (0 ≤ xi, yi ≤ 400)
  - oi,ci: the lower and upper bound on the number of minutes after a node opens that we may enter the node Ai (0 ≤ oi ≤ ci ≤ 1440). Note, then, that we may visit the node at any time between oi and ci.
  - ui: the utility that we get from attending Ai (0 < ui ≤ 27200)
  - ti: the amount of time in minutes that we spend at a node Ai (when we visit Ai, we must spend ti amount of time)

Every number given in the input is an integer

## Output
### The program outputs the following lines
- M: the number of attractions visited
- A list of unique nodes (by number) in the order visited

## Aim
The program should output a feasible sequence of nodes that earns them the most utility. To determine if a sequence is feasible, we begin by describing how we behave on the graph:
- Start at (200, 200) at minute 0 of the day
- We can walk at a rate of 1 unit per minute, and walk from one node to the next in a straight line (which means they may walk right through nodes). We need to wait until the next whole minute to reach their node.
- If Ai is closed, we wait until it opens. When it is open, we spend ti time at Ai. we may experience Ai as long as they get to the location by the time it closes.
  - If Ai closes at minute 17 and they arrive at exactly minute 17, we can still spend the whole ti time there. If we would arrive at minute 17.01, we are unable to do so.
- After we finish visiting the list of nodes, we must head back to (200, 200), which we must arrive at by minute 1440. If we cannot return on time, the sequence is not feasible

## Example Input and Output
```
Example Input:

10
50 350 0 1440 100 20
200 150 0 1440 200 10
200 100 0 1440 20 100
350 50 0 1440 15 40
200 400 0 1440 1000 10
300 150 0 1440 10 1000
400 20 0 1440 100 100
200 275 0 1440 300 30
100 50 0 1440 200 200
225 175 0 1440 100 100

Example Output:
5
5 8 10 2 9
```
