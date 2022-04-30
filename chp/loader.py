import sys

from helper import Disk


def load(filename=None) -> list[Disk]:
    if filename is None:
        print("no files specified")
        sys.exit(1)
    disks: list[Disk] = []
    with open(filename) as f:
        i = 0
        for line in f:
            xs = line.split("\t")
            if len(xs) != 4:
                continue
            uid, x, y, r = int(xs[0]), float(xs[1]), float(xs[2]), float(xs[3])
            d = Disk(uid, x, y, r)
            disks.append(d)
            i += 1
    return disks
