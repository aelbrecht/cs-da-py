import time


def load():
    vertices = {}
    with open("./input/p_hat300-1.clq") as f:
        for line in f:
            if line[0] != "e":
                continue
            v1, v2 = [int(a) for a in line.split(" ")[1:]]
            if v1 not in vertices:
                vertices[v1] = []
            if v2 not in vertices:
                vertices[v2] = []
            vertices[v1].append(v2)
            vertices[v2].append(v1)
    return vertices


def intersection(l1, l2):
    return [v for v in l1 if v in l2]


def clique(us: list, size):
    global maximum
    if len(us) == 0:
        if size > maximum:
            maximum = size
            # new record; save it.
        return
    while len(us) != 0:
        if size + len(us) <= maximum:
            return
        i = us[0]
        us = us[1:]
        clique(intersection(us, edges[i]), size + 1)


if __name__ == '__main__':
    edges = load()
    maximum = 0
    vxs = sorted(list(edges.keys()))
    start_time = time.time()
    clique(vxs, 0)
    elapsed = time.time() - start_time
    print(f"took {elapsed}s")
