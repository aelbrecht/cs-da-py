import random
from typing import Type


class Graph:
    neighbors: list[list[int]]
    edges: list[[int, int]]
    weights: list[int]
    vertices: set[int]
    n: int


def generate_graph(n=10) -> Type[Graph]:
    vertices: list[int] = [0]
    neighbors: list[list[int]] = [[]]
    edges: list[[int, int]] = []
    for i in range(1, n):
        random.shuffle(vertices)
        m = random.randint(0, i)
        xs = vertices[:m]
        neighbors.append(xs)
        for x in xs:
            edges.append([x, i])
            neighbors[x].append(i)
        vertices.append(i)
    weights = [random.randint(1, 1000) for _ in range(0, n)]
    g = Graph
    g.vertices = set(vertices)
    g.neighbors = neighbors
    g.weights = weights
    g.edges = edges
    g.n = n
    return g


if __name__ == '__main__':
    graph = generate_graph()
    print(graph.vertices)
    print(graph.neighbors)
    print(graph.weights)
    print(graph.edges)
