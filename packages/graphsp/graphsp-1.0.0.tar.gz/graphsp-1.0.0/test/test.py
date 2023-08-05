from graphsp import *

# n = 5
# graph = Graph(5, "undirected")
# graph.bulk_link([(0, 4, 5), (0, 1, 1), (1, 4, 3),
#                  (1, 3, 1), (1, 2, 15), (2, 3, 2), (3, 4, 3)])


# fw = FloydWarshall(n, graph)
# print(fw.floyd_warshall())

# dfs = DFS(n, graph)
# print(dfs.dfs(0))

# bfs = BFS(n, graph)
# print(bfs.bfs(0))

# dj = Dijkstra(n, graph)
# print(dj.dijkstra(0))
# n = 3
# g = Graph(4, "undirected")
# g.bulk_link([[0, 1, 1], [0, 2, 1], [2, 0, 1]])
# print(g.detect_cycle())

# graph = Graph(9, "undirected")
# graph.link(0, 1, 4)
# graph.link(0, 7, 8)
# graph.link(1, 2, 8)
# graph.link(1, 7, 11)
# graph.link(2, 3, 7)
# graph.link(2, 8, 2)
# graph.link(2, 5, 4)
# graph.link(3, 4, 9)
# graph.link(3, 5, 14)
# graph.link(4, 5, 10)
# graph.link(5, 6, 2)
# graph.link(6, 7, 1)
# graph.link(6, 8, 6)
# graph.link(7, 8, 7)

# prim = Prim(9, graph)
# print(prim.prim())


# k = Kruskal(9, graph)
# print(k.kruskal())


# g = Graph(5, "directed")
# g.link(0, 1, -1)
# g.link(0, 2, 4)
# g.link(1, 2, 3)
# g.link(1, 3, 2)
# g.link(1, 4, 2)
# g.link(3, 2, 5)
# g.link(3, 1, 1)
# g.link(4, 3, -3)

# bf = BellmanFord(5, g)
# print(bf.bellman_ford(0))

# g1 = Graph(5, "direced")
# g1.link(0, 1)
# g1.link(1, 2)
# g1.link(2, 3)
# g1.link(3, 0)
# g1.link(2, 4)
# g1.link(4, 2)


# g2 = Graph(4, "directed")
# g2.link(0, 1)
# g2.link(1, 2)
# g2.link(2, 3)

# kr = Kosaraju(4, g2)
# print(kr.kosaraju())
