import random
from typing import Type


class Graph:
    edges: list[list[int]]
    weights: list[int]
    vertices: set[int]
    n: int


def generate_graph(n=10) -> Type[Graph]:
    vertices: list[int] = [0]
    edges: list[list[int]] = [[]]
    for i in range(1, n):
        random.shuffle(vertices)
        m = random.randint(0, i)
        neighbors = vertices[:m]
        edges.append(neighbors)
        for v in neighbors:
            edges[v].append(i)
        vertices.append(i)
    weights = [random.randint(1, 1000) for _ in range(0, n)]
    g = Graph
    g.vertices = set(vertices)
    g.edges = edges
    g.weights = weights
    g.n = n
    return g


if __name__ == '__main__':
    g = generate_graph()
    print(g.vertices)
    print(g.edges)
    print(g.weights)
