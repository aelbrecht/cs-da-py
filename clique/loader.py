def load(filename="./input/p_hat300-2.clq") -> dict[int, list[int]]:
    vertices: dict[int, list[int]] = {}
    with open(filename) as f:
        for line in f:
            if line[0] != "e":
                continue
            v1, v2 = [int(a) for a in line.split(" ")[1:]]
            v1 -= 1
            v2 -= 1
            if v1 not in vertices:
                vertices[v1] = []
            if v2 not in vertices:
                vertices[v2] = []
            vertices[v1].append(v2)
            vertices[v2].append(v1)
    return vertices
