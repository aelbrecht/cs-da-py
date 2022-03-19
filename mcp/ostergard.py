import time

from loader import load


def intersection(l1, l2):
    return [v for v in l1 if v in l2]


def clique(us: list, size):
    global maximum, found, c
    if len(us) == 0:
        if size > maximum:
            maximum = size
            # new record; save it.
            found = True
        return
    while len(us) != 0:

        if size + len(us) <= maximum:
            return

        i = us[0]

        if size + c[i] <= maximum:
            return

        us = us[1:]
        clique(intersection(us, edges[i]), size + 1)
        if found is True:
            return


if __name__ == '__main__':
    edges = load()
    maximum = 0
    vxs = sorted(list(edges.keys()))
    n = len(vxs)
    start_time = time.time()
    c = {}
    for k in vxs:
        c[k] = 0
    for j in range(n - 1, -1, -1):
        found = False
        k = vxs[j]
        clique(intersection(vxs[j:], edges[k]), 1)
        c[k] = maximum
    print(maximum)
    elapsed = time.time() - start_time
    print(f"took {elapsed}s")
