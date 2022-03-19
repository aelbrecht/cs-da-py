import random
from typing import Type

from loader import generate_graph, Graph


def cost(c: set[int], g: Type[Graph]) -> int:
    return sum([g.weights[v] for v in c])


def largest_degree(x1: int, x2: int, g: Type[Graph]):
    if len(g.neighbors[x1]) > len(g.neighbors[x2]):
        return x1
    elif len(g.neighbors[x1]) < len(g.neighbors[x2]):
        return x2
    if g.weights[x1] > g.weights[x2]:
        return x1
    else:
        return x2


def construct_wvc(g: Type[Graph]) -> set[int]:
    c = set()
    # e ∈ E
    for [x1, x2] in g.edges:
        # both endpoints of e are not in C
        if x1 not in c and x2 not in c:
            # put the endpoint with larger degree(v)/w(v) into C
            c.add(largest_degree(x1, x2, g))
    # tries ← 0; tries < construct_tries; tries ← tries + 1
    for tries in range(0, construct_tries):
        c_bis = set()
        # for uncovered e ∈ E (in a random order)
        random.shuffle(g.edges)
        for [x1, x2] in g.edges:
            # both endpoints of e are not in C
            if x1 not in c_bis and x2 not in c_bis:
                # put the endpoint with larger degree(v)/w(v) into C′
                c_bis.add(largest_degree(x1, x2, g))
        # C' is better than C then C <- C'
        if cost(c_bis, g) < cost(c, g):
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


def fast_wvc(g: Type[Graph]):
    c = construct_wvc(g)
    c_star = c.copy()

    # TODO


if __name__ == '__main__':
    construct_tries = 100
    gr = generate_graph(30)
    fast_wvc(gr)
