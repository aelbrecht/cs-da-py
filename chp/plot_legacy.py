import sys

import matplotlib.pyplot as plt


def read_csv(file):
    points = list()
    with open(f"./data/{file}.txt") as csv:
        for line in csv.readlines()[1:]:
            p = [float(x) for x in line.split("\t")]
            points.append(p)
    hull = list()
    with open(f"./data/{file}_sol_legacy.txt") as csv:
        is_hull = False
        for line in csv.readlines()[1:]:
            if line == "Hull\n":
                is_hull = True
                continue
            elif not is_hull:
                continue
            p = [float(x) for x in line.split(",")[1:3]]
            hull.append(p)
    return points, hull


def plot_hull(points, hull):
    if len(points) < 250:
        for p in points:
            x, y = p[1], p[2]
            plt.scatter(x, y, s=p[3])
            plt.annotate(f"{int(p[0]) - 1}", (x, y), textcoords="offset points", xytext=(0, 10), ha='center')
    else:
        pts = [[a[1], a[2]] for a in points]
        plt.scatter(*zip(*pts), s=1)
    plt.plot(*zip(*hull), color="lightgreen")
    plt.show()


if __name__ == '__main__':
    ps, hs = read_csv(sys.argv[1])
    plot_hull(ps, hs)
