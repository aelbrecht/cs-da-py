import math
import time

from loader import load


def c_p(k: set, p: int) -> set:
    c = set()
    for i in vertices:
        neighbors = edges[i]
        if len(k.difference(neighbors)) == p:
            c.add(i)
    return c


def greedy_swap(k_0: set):
    k = k_0
    n_it = 0
    n_swap = 0
    last_swap = -1
    threshold = 2 * len(k_0)
    while True:

        tmp = c_p(k, 0)
        if len(tmp) == 0:
            break

        if n_it > start_swap and n_swap < threshold:
            xs = tmp.union(c_p(k, 1))
            xs.discard(last_swap)
            m = -1
            i = -1
            for j in xs:
                v = len(set(edges[j]).union(tmp))
                if v > m:
                    m = v
                    i = j
            if i in tmp:
                k.add(i)
            else:
                es = edges[i]
                l = -1
                for e in es:
                    if e not in k:
                        l = e
                        break
                k.add(i)
                k.discard(l)
                last_swap = l
                n_swap += 1
        else:
            m = -1
            i = -1
            for j in tmp:
                v = len(set(edges[j]).intersection(tmp))
                if v > m:
                    m = v
                    i = j

            k.add(i)
        n_it += 1
    return k


def weight_greedy(w_i: list[float], k_0: set):
    k_i = k_0

    for i in vertices:
        if i not in k_i:  # or k_t
            pass
        elif i in k_i and w_i[i] > (1 / (2 ** (max_weight - 1))):  # or k_t
            w_i[i] /= 2
        elif i in k_i and w_i[i] == (1 / (2 ** (max_weight - 1))):  # or k_t
            w_i[i] = 0

    while True:
        tmp = c_p(k_i, 0)
        if len(tmp) == 0:
            break

        m = -1
        i = -1
        for j in tmp:
            xs = tmp.intersection(edges[j])
            acc = 0
            for k in xs:
                acc += w_i[k]
            if acc > m:
                m = acc
                i = j
        k_i.add(i)

    return k_i


def dags():
    # Phase 1: apply sm_swap and rank nodes
    k_best = set()
    k_i: list[set] = [set()] * len(vertices)
    for i in vertices:
        k_i[i] = greedy_swap({i})
        if len(k_i[i]) > len(k_best):
            k_best = k_i[i]

    # Compute s j = number of cliques in K_1,..., K_n containing j, ∀ j ∈ V ;
    s = [0] * len(vertices)
    for j in vertices:
        for k in k_i:
            if j in k:
                s[j] += 1

    # Select the first δn nodes with smallest si , call this set U ;

    _, sorted_vertices = zip(*sorted(zip(s, vertices)))

    us = set(sorted_vertices[:math.floor(len(vertices) * delta)])

    # Phase 2
    k_t: set = set()
    for i in us:
        w_i = [1.0] * len(vertices)
        for t in range(1, max_iter):
            k_t = weight_greedy(w_i, {i})
            if len(k_t) > len(k_best):
                k_best = k_t
                print(len(k_best), k_best)
            for j in k_t:
                w_i[j] = w_i[j] / 2
                if w_i[j] < (1 / (2 ** (max_weight - 1))):
                    w_i[j] = 0
    return k_best


if __name__ == '__main__':
    edges = load()
    vertices = sorted(list(edges.keys()))

    delta = 0.15
    max_iter = len(edges) // 16
    max_weight = 1
    start_swap = 5  # determined in paper

    start_time = time.time()
    maximum = len(dags())
    elapsed = time.time() - start_time
    print(f"took {elapsed}s")
    print(maximum)
