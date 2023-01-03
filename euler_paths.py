from z3 import *
import numpy as np
# The problem I chose to solve was that of finding an Eulerian path, if one exists, of an arbitrary undirected graph given its adjacency matrix.
# An Eulerian path is defined as a path that traverses every edge in a given graph exactly once. My program is able to detect if such paths exists and then returns an example if they do.
# Eulerians paths get their name from the famous seven bridges of konigsberg problem that was solved by Euler. The problem is an example of a graph that has no Eulerian paths.
# The proof of this result can be thought of as the birthplace of graph theory and topology, which is what makes this problem so important.
# The main difficulty I faced in solving this problem was making the code usable for an arbitrary graph. 
# If my goal were to find an eulerian path for a specific graph I could have defined "visitable vertices" for each vertex directly using constraints.
# Algorithms have been created to find an Eulerian path, such as Fleury's algorithm and Hierholzer's algorithm.
# However, these algorithms aren't equal in complexity; Fleury's algorithm has a complexity of O((V+E)^2), or just O(E^2) for a connected graph*, while Hierholzer's algorithm finds a path in O(V+E) time*.
# Both of these algorithms operate by navigating the graph and removing edges as they go, storing visited nodes and the currently constructed path as they go.
# By contrast my method precomputes all of the constraints before a single edge in the path.
# As far as I can tell my code is O((V+E)^2) but it is hard to tell given that I am calling the z3 solver. Even without this added complexity my code is sub-optimal.
# This is in part due to the fact that I chose to have my input as an adjacency matrix for visual clarity. 
# For instance, if I were to remake the program such that the input was simply a list of connected vertices then I could remove the nexted for loops which would greatly reduce complexity.
# References:
# *https://en.wikipedia.org/wiki/Eulerian_path

# Define functions.
## P will store the vertices visited in the Eulerian path.
## t is used as a placeholder to assign vertices to arbitrary points in the path. This is explained in more detail before the constraints section.
P = Function('P', IntSort(), IntSort())
t = Function('t', IntSort(), IntSort())

# Create a Z3 solver instance.
s = Solver()

# Set number of vertices and adjacency matrix.
## The example graph I decided to use has a loop edge, vertices connected by multiple edges and 2 vertices of odd degree (meaning that there exists an Eulerian path but not an Eulerian cycle).
## The intention of choosing such a graph was to show that the code is robust to many types of graphs.
adj = np.matrix([[0,1,0,0,0,1],[1,0,1,1,2,0],[0,1,0,0,0,1],[0,1,0,2,1,0],[0,2,0,1,0,0],[1,0,1,0,0,0]])
n = np.shape(adj)[0]
print(adj)

# Set constraints.
## The first set of for loops introduce the constraint that if (i,j) is not 0 in the adjacency matrix then i followed by j or j followed by i must be somewhere in the eulerian path as every edge must be traversed.
## Furthermore, if there are two vertices that are connected g times then the pair i,j or j,i must appear g times in the path.
## As the graph is undirected, I calculate the constraints using only the upper right triangle of the matrix to save time.
## The second set of for loops uses the t variable to assert that each edge is only traversed once.
## It also asserts the length of the Euler path using the counting variable k that was used to count the number of edges.
## As can be seen in the output, the t function counts the order in which the vertices visited in the path are read from the adjacency matrix. 
## These vertices are then reordered to fit the constraints and stored in P.
k = 0
for i in range(n):
    for j in range(i,n):
        if adj[i,j] != 0:
            for g in range(adj[i,j]):
                s.add(Or(And(P(t(k))==i,P(t(k)+1)==j),And(P(t(k))==j,P(t(k)+1)==i)))
                k += 1
for i in range(k):
    s.add(t(i)<=(k-1),t(i)>=0)
    for j in range(k):
        if i==j:
            continue
        s.add(t(i)!=t(j))
    

# Print all constraints.
print(s)

# Solve the asserted constraints.
r = s.check()
print(r)

# Exit from the program if unsatisfiable.
if r == unsat:
	exit()

# Return a solution.
m = s.model()

# Display the solution in the symbolic expression (i.e. SMT-LIB2 format).
print(m.sexpr())

# Print results
results = []
for i in range(k+1):
    results.append(m.evaluate(P(i)).as_long())
print("An Euler path is given by: ", results)

# [[0 1 0 0 0 1]
#  [1 0 1 1 2 0]
#  [0 1 0 0 0 1]
#  [0 1 0 2 1 0]
#  [0 2 0 1 0 0]
#  [1 0 1 0 0 0]]
# [Or(And(P(t(0)) == 0, P(t(0) + 1) == 1),
#     And(P(t(0)) == 1, P(t(0) + 1) == 0)),
#  Or(And(P(t(1)) == 0, P(t(1) + 1) == 5),
#     And(P(t(1)) == 5, P(t(1) + 1) == 0)),
#  Or(And(P(t(2)) == 1, P(t(2) + 1) == 2),
#     And(P(t(2)) == 2, P(t(2) + 1) == 1)),
#  Or(And(P(t(3)) == 1, P(t(3) + 1) == 3),
#     And(P(t(3)) == 3, P(t(3) + 1) == 1)),
#  Or(And(P(t(4)) == 1, P(t(4) + 1) == 4),
#     And(P(t(4)) == 4, P(t(4) + 1) == 1)),
#  Or(And(P(t(5)) == 1, P(t(5) + 1) == 4),
#     And(P(t(5)) == 4, P(t(5) + 1) == 1)),
#  Or(And(P(t(6)) == 2, P(t(6) + 1) == 5),
#     And(P(t(6)) == 5, P(t(6) + 1) == 2)),
#  Or(And(P(t(7)) == 3, P(t(7) + 1) == 3),
#     And(P(t(7)) == 3, P(t(7) + 1) == 3)),
#  Or(And(P(t(8)) == 3, P(t(8) + 1) == 3),
#     And(P(t(8)) == 3, P(t(8) + 1) == 3)),
#  Or(And(P(t(9)) == 3, P(t(9) + 1) == 4),
#     And(P(t(9)) == 4, P(t(9) + 1) == 3)),
#  t(0) <= 9,
#  t(0) >= 0,
#  t(0) != t(1),
#  t(0) != t(2),
#  t(0) != t(3),
#  t(0) != t(4),
#  t(0) != t(5),
#  t(0) != t(6),
#  t(0) != t(7),
#  t(0) != t(8),
#  t(0) != t(9),
#  t(1) <= 9,
#  t(1) >= 0,
#  t(1) != t(0),
#  t(1) != t(2),
#  t(1) != t(3),
#  t(1) != t(4),
#  t(1) != t(5),
#  t(1) != t(6),
#  t(1) != t(7),
#  t(1) != t(8),
#  t(1) != t(9),
#  t(2) <= 9,
#  t(2) >= 0,
#  t(2) != t(0),
#  t(2) != t(1),
#  t(2) != t(3),
#  t(2) != t(4),
#  t(2) != t(5),
#  t(2) != t(6),
#  t(2) != t(7),
#  t(2) != t(8),
#  t(2) != t(9),
#  t(3) <= 9,
#  t(3) >= 0,
#  t(3) != t(0),
#  t(3) != t(1),
#  t(3) != t(2),
#  t(3) != t(4),
#  t(3) != t(5),
#  t(3) != t(6),
#  t(3) != t(7),
#  t(3) != t(8),
#  t(3) != t(9),
#  t(4) <= 9,
#  t(4) >= 0,
#  t(4) != t(0),
#  t(4) != t(1),
#  t(4) != t(2),
#  t(4) != t(3),
#  t(4) != t(5),
#  t(4) != t(6),
#  t(4) != t(7),
#  t(4) != t(8),
#  t(4) != t(9),
#  t(5) <= 9,
#  t(5) >= 0,
#  t(5) != t(0),
#  t(5) != t(1),
#  t(5) != t(2),
#  t(5) != t(3),
#  t(5) != t(4),
#  t(5) != t(6),
#  t(5) != t(7),
#  t(5) != t(8),
#  t(5) != t(9),
#  t(6) <= 9,
#  t(6) >= 0,
#  t(6) != t(0),
#  t(6) != t(1),
#  t(6) != t(2),
#  t(6) != t(3),
#  t(6) != t(4),
#  t(6) != t(5),
#  t(6) != t(7),
#  t(6) != t(8),
#  t(6) != t(9),
#  t(7) <= 9,
#  t(7) >= 0,
#  t(7) != t(0),
#  t(7) != t(1),
#  t(7) != t(2),
#  t(7) != t(3),
#  t(7) != t(4),
#  t(7) != t(5),
#  t(7) != t(6),
#  t(7) != t(8),
#  t(7) != t(9),
#  t(8) <= 9,
#  t(8) >= 0,
#  t(8) != t(0),
#  t(8) != t(1),
#  t(8) != t(2),
#  t(8) != t(3),
#  t(8) != t(4),
#  t(8) != t(5),
#  t(8) != t(6),
#  t(8) != t(7),
#  t(8) != t(9),
#  t(9) <= 9,
#  t(9) >= 0,
#  t(9) != t(0),
#  t(9) != t(1),
#  t(9) != t(2),
#  t(9) != t(3),
#  t(9) != t(4),
#  t(9) != t(5),
#  t(9) != t(6),
#  t(9) != t(7),
#  t(9) != t(8)]
# sat
# (define-fun P ((x!0 Int)) Int
#   (ite (= x!0 1) 0
#   (ite (= x!0 3) 2
#   (ite (= x!0 10) 4
#   (ite (= x!0 2) 5
#   (ite (= x!0 7) 3
#   (ite (= x!0 5) 4
#   (ite (= x!0 6) 3
#   (ite (= x!0 8) 3
#     1)))))))))
# (define-fun t ((x!0 Int)) Int
#   (ite (= x!0 1) 1
#   (ite (= x!0 2) 3
#   (ite (= x!0 3) 8
#   (ite (= x!0 4) 9
#   (ite (= x!0 5) 4
#   (ite (= x!0 6) 2
#   (ite (= x!0 7) 7
#   (ite (= x!0 8) 6
#   (ite (= x!0 9) 5
#     0))))))))))
# An Euler path is given by:  [1, 0, 5, 2, 1, 4, 3, 3, 3, 1, 4]
