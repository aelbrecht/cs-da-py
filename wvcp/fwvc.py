import random
import time
from typing import Type

from loader import generate_graph, Graph


def cost(c: set[int], e_weights: list[int], g: Type[Graph]) -> int:
    return sum([e_weights[i] for i in uncovered_edges(c, g)])


def cost_vertex(c: set[int], g: Type[Graph]) -> int:
    return sum([g.weights[v] for v in c])


def largest_degree_weight(x1: int, x2: int, g: Type[Graph]) -> int:
    if len(g.neighbors[x1]) / g.weights[x1] > len(g.neighbors[x2]) / g.weights[x2]:
        return x1
    else:
        return x2


def d_score(c: set[int], v: int, edge_w: list[int], g: Type[Graph]) -> int:
    c_bis = c.copy()
    c_bis.remove(v)
    return cost(c, edge_w, g) - cost(c_bis, edge_w, g)


def loss(c: set[int], v: int, edge_w: list[int], g: Type[Graph]) -> float:
    return abs(d_score(c, v, edge_w, g)) / g.weights[v]


def construct_wvc(g: Type[Graph]) -> set[int]:
    c = set()
    # e ∈ E
    for [x1, x2] in g.edges:
        # both endpoints of e are not in C
        if x1 not in c and x2 not in c:
            # put the endpoint with larger degree(v)/w(v) into C
            c.add(largest_degree_weight(x1, x2, g))
    # tries ← 0; tries < construct_tries; tries ← tries + 1
    for tries in range(0, construct_tries):
        c_bis = set()
        # for uncovered e ∈ E (in a random order)
        random.shuffle(g.edges)
        for [x1, x2] in g.edges:
            # both endpoints of e are not in C
            if x1 not in c_bis and x2 not in c_bis:
                # put the endpoint with larger degree(v)/w(v) into C′
                c_bis.add(largest_degree_weight(x1, x2, g))
        # C' is better than C then C <- C'
        if cost_vertex(c_bis, g) < cost_vertex(c, g):
            c = c_bis

    # harm_value is an array containing values for each vector
    # we calculate effect of removing a vertex and store its value
    # if it is 0 afterwards we can safely remove this vertex
    harm_value = [0] * g.n
    for [x1, x2] in g.edges:
        # only one endpoint v of e belongs to C
        if (x1 in c and x2 in c) or (x1 not in c and x2 not in c):
            continue
        if x1 in c:
            harm_value[x1] += 1
        else:
            harm_value[x2] += 1

    for v in c:
        if harm_value[v] == 0:
            c.remove(v)
            for u in g.neighbors[v]:
                harm_value[u] += 1

    return c


def is_edge_uncovered(c: set[int], g: Type[Graph]) -> bool:
    for [x1, x2] in g.edges:
        if x1 not in c and x2 not in c:
            return True
    return False


def uncovered_edges(c: set[int], g: Type[Graph]) -> list[int]:
    for i, [x1, x2] in enumerate(g.edges):
        if x1 not in c and x2 not in c:
            yield i


def fast_wvc(g: Type[Graph]):
    c = construct_wvc(g)
    c_star = c.copy()

    edge_w = [1] * len(g.edges)
    conf_change = [1] * len(g.vertices)

    # calculate gain and loss of vertices?
    start_time = time.time()
    elapsed_time = 0
    tabu_list = [0] * len(g.vertices)
    while elapsed_time < cutoff:
        elapsed_time = time.time() - start_time

        # choose a vertex w with minimum loss from C, breaking ties in favor of the oldest one;
        w = -1
        minimum = 1e10
        for u in c:
            y = loss(c, u, edge_w, g)
            if y < minimum:
                w = u
                minimum = y
        c.remove(w)
        conf_change[w] = 0
        for z in g.neighbors[w]:
            conf_change[z] = 1

        # choose a vertex u with tabu[u] = 0 from C according to BMS strategy, breaking ties in favor of the oldest one;
        minimum = 1e10
        u = -1
        k = 0
        for i, x in enumerate(tabu_list):
            if i not in c:
                continue
            if k > 10:
                break
            if x == 0:
                y = loss(c, i, edge_w, g)
                if y < minimum:
                    u = i
                    minimum = y
                k += 1
        c.remove(u)
        conf_change[u] = 0
        for z in g.neighbors[u]:
            conf_change[z] = 1

        # some edge is uncovered by C
        tabu_list = [0] * len(g.vertices)
        while is_edge_uncovered(c, g):
            # choose a vertex v, whose con fChange(v ) = 1, with maximum gain from V \ C, breaking ties in favor of the
            # oldest one;
            u = -1
            maximum = 0
            candidates = g.vertices.difference(c)
            for i, y in enumerate(conf_change):
                if i not in candidates:
                    continue
                if y == 1:
                    cost_pre = cost_vertex(c, g)
                    c_new = c.copy()
                    c_new.add(i)
                    cost_ante = cost_vertex(c_new, g)
                    gain = cost_ante - cost_pre
                    if gain > maximum:
                        u = i
                        maximum = gain

            c.add(u)
            tabu_list[u] = 1

            for n in g.neighbors[u]:
                conf_change[n] = 1

            uncovered = uncovered_edges(c, g)
            for e in uncovered:
                edge_w[e] += 1
                [x, y] = g.edges[e]
                conf_change[x] = 1
                conf_change[y] = 1

        # remove redundant vertices from C;
        if cost(c, edge_w, g) < cost(c_star, edge_w, g):
            c_star = c

    return c


if __name__ == '__main__':
    construct_tries = 100
    gr = generate_graph(30)
    cutoff = 15
    result = fast_wvc(gr)
    coverage = set()
    for vert in result:
        coverage.add(vert)
        for neigh in gr.neighbors[vert]:
            coverage.add(neigh)

    print(f"expected {len(gr.vertices)} got {len(coverage)} with weight {sum([gr.weights[i] for i in result])}")
