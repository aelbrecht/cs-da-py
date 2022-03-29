import random
from typing import Type


class Graph:
    neighbors: list[list[int]]
    edges: list[[int, int]]
    weights: list[int]
    vertices: set[int]
    n: int


def load_graph(filename="./input/self-made-1") -> Type[Graph]:
    vertices: list[int] = []
    neighbors: list[list[int]] = []
    edges: list[[int, int]] = []
    weights: list[int] = []
    with open(filename + ".vertices") as f:
        i = 0
        for line in f:
            if len(line) == 0:
                continue
            vertices.append(i)
            neighbors.append([])
            weights.append(int(line.strip()))
            i += 1
    with open(filename + ".edges") as f:
        for line in f:
            if len(line) == 0:
                continue
            v1, v2 = [int(a) for a in line.strip().split(" ")]
            v1 -= 1
            v2 -= 1
            edges.append([v1, v2])
            neighbors[v1].append(v2)
            neighbors[v2].append(v1)
    g = Graph
    g.vertices = set(vertices)
    g.neighbors = neighbors
    g.weights = weights
    g.edges = edges
    g.n = len(vertices)
    return g


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
