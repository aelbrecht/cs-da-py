import math
import random
import sys
from time import perf_counter

from helper import Disk, Line, Point, Sliver
from loader import load


def find_left_most_point(disks: list[Disk], reverse: bool = False) -> (Disk, Point):
    sign = -1 if not reverse else 1
    best = disks[0]
    for curr in disks:
        left_most_x = best.x() + best.radius() * sign
        left_curr_x = curr.x() + curr.radius() * sign
        if (left_curr_x < left_most_x and not reverse) or (left_curr_x > left_most_x and reverse):
            best = curr
        elif left_curr_x == left_most_x:
            if (curr.y() > best.y() and not reverse) or (curr.y() < best.y() and reverse):
                best = curr
            elif curr.y() == best.y() and curr.radius() > best.radius():
                best = curr

    return best, Point(best.x() + best.radius() * sign, best.y())


def quickhull(disks: list[Disk]) -> list[Disk]:
    assert len(disks) > 1

    # find most extreme points
    leftest_disk, top_left_point = find_left_most_point(disks)
    rightest_disk, right_bottom_point = find_left_most_point(disks, reverse=True)  # reverse inverts x- and y-axis

    # split dataset into two sets, overlap is allowed
    oriented_line = Line(top_left_point, right_bottom_point)
    left_set: list[Disk] = []
    right_set: list[Disk] = []
    for curr in disks:
        d = oriented_line.signed_distance(curr.point())
        if d <= curr.radius():
            right_set.append(curr)
        if d >= -curr.radius():
            left_set.append(curr)

    # evaluate each set, order is important
    results: list[Disk] = []
    find_hull(right_set, leftest_disk, rightest_disk, top_left_point, right_bottom_point, results)
    find_hull(left_set, rightest_disk, leftest_disk, right_bottom_point, top_left_point, results)

    # remove consecutive points with same id
    last_id = -1
    filtered: list[Disk] = []
    for d in results:
        if d.id() == last_id:
            continue
        last_id = d.id()
        filtered.append(d)

    return filtered


def find_farthest_point(disk: Disk, oriented_line: Line) -> Point:
    negative = -oriented_line.normal_vector()
    res: Point = negative.unit_vector() * disk.radius()
    farthest_point = res + disk
    return farthest_point


def find_highest_triangle_apex(disks: list[Disk], oriented_line: Line, oriented_is_support: bool = False,
                               pre_apex: Disk = None, post_apex: Disk = None) -> list[(Point, Disk)]:
    results: list[(Point, Disk)] = []
    largest_max_perp_dist = 0.0
    for curr in disks:
        if oriented_is_support and (curr == oriented_line.start or curr == oriented_line.end):
            continue
        max_perp_dist = curr.radius() - oriented_line.signed_distance(curr)
        if max_perp_dist > largest_max_perp_dist:
            largest_max_perp_dist = max_perp_dist
            results = [(find_farthest_point(curr, oriented_line), curr)]
        elif max_perp_dist == largest_max_perp_dist:
            results.append((find_farthest_point(curr, oriented_line), curr))

    # when the oriented line is used as support, make sure candidates exist
    if oriented_is_support and largest_max_perp_dist == 0:
        if pre_apex is not None:
            results.append((oriented_line.start, pre_apex))
        if post_apex is not None:
            results.append((oriented_line.end, post_apex))

    return results


def find_largest_apex_disk(candidates: list[(Point, Disk)], selected: int) -> (list[Disk], Disk):
    largest_disk: Disk = candidates[selected][1]
    largest_disk_index: int = selected
    contained: list[int] = []  # keep track of disks being contained by a larger one
    for i, c in enumerate(candidates):
        curr: Disk = c[1]
        if curr == largest_disk:
            continue
        if curr.contains(largest_disk):
            contained.append(largest_disk_index)
            largest_disk = curr
            largest_disk_index = i
        elif largest_disk.contains(curr):
            contained.append(i)
    return contained, largest_disk


def pick_one_triangle_apex(candidates: list[(Point, Disk)]) -> (Point, Disk):
    # pick a random candidate
    pick = random.randint(0, len(candidates) - 1)
    triangle_apex: Point = candidates[pick][0]
    # check if this candidate isn't trash
    contained, apex_disk = find_largest_apex_disk(candidates, pick)
    while len(contained) != 0:
        i = contained.pop()
        del candidates[i]
    return triangle_apex, apex_disk  # triangle_apex is returned anyway?


def disk_is_member_of_expanded(candidate: Disk, oriented_line: Line) -> bool:
    dist_line_to_disk = oriented_line.signed_distance(candidate)
    orthogonal_line_at_start = oriented_line.perpendicular(oriented_line.start)
    orthogonal_line_at_end = oriented_line.perpendicular(oriented_line.end)
    if dist_line_to_disk <= -candidate.radius():
        # negative or on-negative
        return orthogonal_line_at_start.signed_distance(
            candidate) < -candidate.radius() and orthogonal_line_at_end.signed_distance(
            candidate) > candidate.radius()
    elif -candidate.radius() < dist_line_to_disk < candidate.radius():
        # crossing
        return orthogonal_line_at_start.signed_distance(
            candidate) < 0 and orthogonal_line_at_end.signed_distance(candidate) > 0
    elif dist_line_to_disk == candidate.radius():
        # on-positive
        return orthogonal_line_at_start.signed_distance(
            candidate) < 0 and orthogonal_line_at_end.signed_distance(candidate) > 0
    else:
        # positive
        return False


def find_expanded_disks(disks: list[Disk], oriented_line: Line, d1: Disk, d2: Disk) -> list[Disk]:
    output: list[Disk] = []
    # do not check disks if the oriented line is a point as calculations will be meaningless
    if not oriented_line.is_point():
        for curr in disks:
            if curr == d1 or curr == d2:
                continue
            if disk_is_member_of_expanded(curr, oriented_line):
                output.append(curr)
    # make sure original disks are included
    if d1 == d2:
        output.append(d1)
    else:
        output.append(d1)
        output.append(d2)
    return output


def triangle_is_sliver(n_disk: int, n_front: int, n_back: int, pre_apex: Disk, post_apex: Disk) -> bool:
    return (pre_apex != post_apex) and ((n_front == n_disk and n_back == 1) or (n_front == 1 and n_back == n_disk))


def find_oriented_tangent_line_segment(d1: Disk, d2: Disk):
    if d1.radius() == 0 and d2.radius() == 0:
        return Line(d1, d2)
    tangent1, tangent2 = find_tangents_between_circles(d1, d2)
    dist = tangent1.signed_distance(d1) + tangent1.signed_distance(d2)
    if dist > 0:
        return tangent1
    else:
        return tangent2


def find_oriented_between_circles(c1: Disk, c2: Disk) -> (list[float], list[float]):
    # make sure c1 is the larger circle
    if c1.radius() < c2.radius():
        c1, c2 = c2, c1
    # init stuff
    dir_vec: Point = c1 - c2
    radius_diff = c1.radius() - c2.radius()
    length = dir_vec.magnitude()
    sine = radius_diff / length
    cosine = math.sqrt(length * length - radius_diff * radius_diff) / length
    # rotate theta | -theta
    norm1 = Point(dir_vec.x() * cosine - dir_vec.y() * sine, dir_vec.x() * sine + dir_vec.y() * cosine)
    norm2 = Point(dir_vec.x() * cosine - dir_vec.y() * sine, dir_vec.y() * cosine + dir_vec.x() * sine)
    norm1 = norm1.unit_vector()
    norm2 = norm2.unit_vector()
    # rotate -pi/2 | pi/2
    norm1 = Point(norm1.y(), -1 * norm1.x())
    norm2 = Point(-1 * norm2.y(), norm2.x())
    # compute resulting equations
    r1 = [norm1.x(), norm1.y(), -1 * norm1.x() * c2.x() - norm1.y() * c2.y() + c2.radius()]
    r2 = [norm2.x(), norm2.y(), -1 * norm2.x() * c2.x() - norm2.y() * c2.y() + c2.radius()]
    return r1, r2


def find_tangent_point(circle: Disk, eq: [float, float, float]) -> Point:
    x = circle.x()
    y = circle.y()
    a = eq[0]
    b = eq[1]
    a2_b2 = a * a + b * b
    # fill in equation to find tangent point
    tangent_point: Point
    if a2_b2 == 1:  # save cpu cycles
        tangent_point = Point(-a * (eq[0] * x + eq[1] * y + eq[2]) + x, -b * (eq[0] * x + eq[1] * y + eq[2]) + y)
    else:
        tangent_point = Point(-a * (eq[0] * x + eq[1] * y + eq[2]) / a2_b2 + x,
                              -b * (eq[0] * x + eq[1] * y + eq[2]) / a2_b2 + y)
    return tangent_point


def find_tangents_between_circles(c1: Disk, c2: Disk) -> (Line, Line):
    [t1, t2] = find_oriented_between_circles(c1, c2)
    d1_tan_points: [Point, Point]
    d2_tan_points: [Point, Point]
    if c1.radius() != 0:  # save cpu cycles when using points
        d1_tan_points = [find_tangent_point(c1, t1), find_tangent_point(c1, t2)]
    else:
        d1_tan_points = [c1, c1]
    if c2.radius() != 0:
        d2_tan_points = [find_tangent_point(c2, t1), find_tangent_point(c2, t2)]
    else:
        d2_tan_points = [c2, c2]
    return Line(d1_tan_points[0], d2_tan_points[0]), Line(d1_tan_points[1], d2_tan_points[1])


def regularize_sliver(disks: list[Disk], hull_p: Point, hull_q: Point, pre_apex: Disk, post_apex: Disk):
    supporting_tangent = find_oriented_tangent_line_segment(pre_apex, post_apex)
    candidates: list[(Point, Disk)] = find_highest_triangle_apex(disks, supporting_tangent, True, pre_apex, post_apex)

    # pick first candidate and compute height in new triangle
    candidate_apex: Disk = candidates[0][1]
    height_of_triangle = candidate_apex.radius() - supporting_tangent.signed_distance(candidate_apex)

    # keep track of positive
    sliver_case: Sliver

    if height_of_triangle == 0:

        # todo can be cleaner
        # remove pre- and post-apex disks and contained disks in one of the two from candidate apex disks if exist
        # remove contained disks from input disks
        rm_list = []
        rm_dict = {}
        for i, c in enumerate(candidates):
            d: Disk = c[1]
            if d == pre_apex or d == post_apex or pre_apex.contains(d) or post_apex.contains(d):
                rm_list.append(i)
                rm_dict[d.id()] = True
        rm_list.reverse()
        for i in rm_list:
            del candidates[i]
        rm_list = []
        for i, d in enumerate(disks):
            if d.id() in rm_dict:
                rm_list.append(i)
        rm_list.reverse()
        for i in rm_list:
            del disks[i]

        # handle cases A and B
        if len(candidates) == 1:
            sliver_case = Sliver.SLIVER_CASE_A
        else:
            sliver_case = Sliver.SLIVER_CASE_B
    else:
        # case "C" does not show up in coverage but is mentioned in the paper and source
        if len(candidates) == 1:
            sliver_case = Sliver.SLIVER_CASE_C1
        else:
            sliver_case = Sliver.SLIVER_CASE_C2

    # compute pivot point and disk
    if sliver_case == Sliver.SLIVER_CASE_A:
        triangle_apex_disk_pairs = [(supporting_tangent.start, pre_apex), (supporting_tangent.end, post_apex)]
        pivot_point, pivot_disk = pick_one_triangle_apex(triangle_apex_disk_pairs)
    elif sliver_case == Sliver.SLIVER_CASE_B:
        if len(candidates) == 1:
            pivot_point, pivot_disk = candidates[0]
        else:
            pivot_point, pivot_disk = pick_one_triangle_apex(candidates)
    elif sliver_case == Sliver.SLIVER_CASE_C1:
        pivot_point, pivot_disk = candidates[0]
    elif sliver_case == Sliver.SLIVER_CASE_C2:
        pivot_point, pivot_disk = pick_one_triangle_apex(candidates)
    else:
        sys.exit(1)

    # create new disk sets by splitting the original disks set
    disks_front = find_expanded_disks(disks, Line(hull_p, pivot_point), pre_apex, pivot_disk)
    disks_back = find_expanded_disks(disks, Line(pivot_point, hull_q), pivot_disk, post_apex)
    return disks_front, disks_back, pivot_disk, pivot_point


def find_hull(disks: list[Disk], pre_apex: Disk, post_apex: Disk, pre_hp: Point, post_hp: Point, results: list[Disk]):
    if len(disks) == 1:
        results.append(pre_apex)
        return
    elif len(disks) == 2 and (pre_apex != post_apex):
        results.append(pre_apex)
        results.append(post_apex)
        return

    # find list of candidate pairs
    oriented_line = Line(pre_hp, post_hp)
    candidates: list[(Point, Disk)] = find_highest_triangle_apex(disks, oriented_line)

    # select one candidate
    pivot_point: Point
    pivot_disk: Disk
    if len(candidates) == 1:
        pivot_point, pivot_disk = candidates[0]
    else:
        pivot_point, pivot_disk = pick_one_triangle_apex(candidates)

    # split disks into two datasets
    oriented_front_line = Line(pre_hp, pivot_point)
    disks_front = find_expanded_disks(disks, oriented_front_line, pre_apex, pivot_disk)
    oriented_back_line = Line(pivot_point, post_hp)
    disks_back = find_expanded_disks(disks, oriented_back_line, pivot_disk, post_apex)

    # handle rare case that causes an infinite loop if not handled
    if triangle_is_sliver(len(disks), len(disks_front), len(disks_back), pre_apex, post_apex):
        disks_front.clear()
        disks_back.clear()
        disks_front, disks_back, pivot_disk, pivot_point = regularize_sliver(disks, pre_hp, post_hp, pre_apex,
                                                                             post_apex)

    # iterate
    find_hull(disks_front, pre_apex, pivot_disk, pre_hp, pivot_point, results)
    find_hull(disks_back, pivot_disk, post_apex, pivot_point, post_hp, results)


if __name__ == '__main__':
    files = sys.argv[1:]
    for fn in files:
        # load dataset
        print(f"starting {fn}")
        dxs = load(filename=f"./data/{fn}.txt")

        # run benchmark
        t1_start = perf_counter()
        result = quickhull(dxs)
        t1_stop = perf_counter()

        # export and print result
        print(f"-> hull contains {len(result)} disks")
        print(f"finished in {round((t1_stop - t1_start) * 1000, 3)}ms\n", )
        with open(f"./data/{fn}_sol.txt", "w+") as f:
            f.write(f"{len(result)}\n")
            f.writelines([f"{p.id() + 1}\t{p.x()}\t{p.y()}\t{p.radius()}\n" for p in result])
