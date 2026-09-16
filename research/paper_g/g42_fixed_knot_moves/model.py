"""Fixed-knot lattice-ring Monte Carlo engine for the g42 sandbox.

Frozen preflight source (Paper G cycle 42, 2026-09-14): learned proposal
probabilities over certified segment moves for fixed-knot polymer equilibrium
collapse statistics at matched total cost. The engine samples closed
self-avoiding walks of fixed length N on the cubic lattice Z^3 under a contact
energy E = -C (C = number of non-adjacent nearest-neighbour vertex pairs), with
the knot type of the ring enforced exactly by an integer Alexander-determinant
certificate evaluated on the candidate conformation.

Determinism: the only randomness source is the pure-integer PCG64-XSL-RR
generator implemented below (128-bit state, Python integers). Every draw is
consumed in a fixed order, so a from-scratch rerun of the same config
reproduces every deterministic report field bit-exactly; only the ``timing``
sub-dict may vary.

Engine 1.1.0 changes (preflight, before any sandbox authorization): the
graceful ``certification_ambiguous`` terminal described below, second-half
(tail) autocorrelation statistics for a transient-robust screening criterion,
and pivot-proposal ambiguity handling that no longer swallows non-ambiguity
certification errors. No 1.0.0 code path consumed randomness differently: the
new branches draw no variates and are unreachable on trajectories that never
hit certification ambiguity, so the RNG stream is unchanged by construction;
the replay fingerprint (the 1.0.0-crashing probe unit terminating at the
identical trajectory point) supports this. No archived 1.0.0 report exists to
compare field-by-field.

Engine 1.1.1 changes (pre-authorization audit fixes): overflow-clamped
Metropolis acceptance (a mathematically certain acceptance no longer raises
OverflowError at very low temperature), per-bucket positive-weight validation
for context policies (a zero-weight bucket now fails validation instead of
aborting mid-run), and the ``rg2_var_tail`` degenerate-tail marker consumed
by the frozen exclusion rule. The acceptance expression is unchanged in every
case where 1.1.0 did not raise.

Frozen nonclaims:
- No ergodicity or mixing theorem is claimed for the move library. The library
  is reversible (corner flips are involutions; every pivot's inverse pivot is
  drawable with the same probability), but irreducibility within a knot class
  is unproven and all mixing comparisons are empirical.
- Lattice truth only. Lattice and continuum results cannot be pooled.
- The certificate |Delta(-1)| separates exactly the frozen classes
  {0_1: 1, 3_1: 3, 4_1: 5}. Any other determinant fails the unit closed; the
  engine never guesses. A projection tie in every frozen direction rejects a
  pivot proposal (ambiguity_rejected). An accepted state that no frozen
  direction can certify at a runtime invariant check terminates the unit with
  completed_reason "certification_ambiguous" and the samples collected so far
  (engine 1.1.0; 1.0.0 raised instead, killing the branch container — one
  container runs every unit of a branch — and quarantining the sandbox under
  the no-retry stop rule).

Topology-preservation facts used (proof sketches; full argument in the
preflight record):
- Corner flip b -> b' = a + c - b moves one vertex across the unit square with
  corners a, b, c, b'. A unit lattice square contains exactly its four corner
  lattice points, and no lattice edge meets its open interior, so after the b'
  occupancy check the swept square is disjoint from the rest of the ring and
  the move is an isotopy. Per-flip certification is therefore unnecessary;
  the engine re-certifies periodically as a runtime invariant.
- Padding decoration u -> u+g -> u+g+e -> v replacing edge (u, u+e) sweeps the
  same kind of unit square and is an isotopy by the same argument.
- Pivot proposals may change the knot type and are certified per proposal.
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from fractions import Fraction
from typing import Any

Vertex = tuple[int, int, int]

ENGINE_VERSION = "g42_fixed_knot_moves_engine_1.1.1"
INITSEQ_EXPLORATION = 0x4734325F6578706C  # b"G42_expl" 64-bit stream tag
KNOT_DETERMINANTS = {"0_1": 1, "3_1": 3, "4_1": 5}
PROJECTION_DIRECTIONS: tuple[tuple[int, int, int], ...] = (
    (1, 2, 3),
    (2, 3, 5),
    (3, 4, 7),
    (1, 3, 4),
)
FAMILIES = ("corner", "pivot", "self_loop")
_NEIGHBOUR_STEPS: tuple[Vertex, ...] = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
_DECORATION_ORDER: tuple[Vertex, ...] = (
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (-1, 0, 0),
    (0, -1, 0),
    (0, 0, -1),
)
_BRAID_WORDS: dict[str, tuple[tuple[int, int], ...]] = {
    "3_1": ((0, 1), (0, 1), (0, 1)),
    "4_1": ((0, 1), (1, -1), (0, 1), (1, -1)),
}
_BRAID_STRANDS: dict[str, int] = {"3_1": 2, "4_1": 3}


class EngineError(RuntimeError):
    """Fail-closed abort for any engine invariant violation."""


class CertificationAmbiguityError(EngineError):
    """The projection under a fixed direction has an unresolved tie."""


# ---------------------------------------------------------------------------
# PCG64-XSL-RR (128-bit state, 64-bit output), pure integer implementation.
# Constants follow the PCG reference (O'Neill); setseq seeding: state = 0,
# inc = (initseq << 1) | 1, one step, state += initstate, two more steps.
# Output: xorshift-low of the two state halves, rotated right by the top six
# state bits.
# ---------------------------------------------------------------------------

_MASK128 = (1 << 128) - 1
_MASK64 = (1 << 64) - 1
_PCG_MULT = 0x2360ED051FC65DA44F854E86378ACA9C98DBE14055BCC1F0B


class PCG64:
    def __init__(self, initstate: int, initseq: int) -> None:
        if not 0 <= initstate <= _MASK128 or not 0 <= initseq <= _MASK64:
            raise EngineError("pcg seed out of range")
        self._inc = ((initseq << 1) | 1) & _MASK128
        self._state = 0
        self._draws = 0
        self._step()
        self._state = (self._state + initstate) & _MASK128
        self._step()
        self._step()

    def _step(self) -> None:
        self._state = (self._state * _PCG_MULT + self._inc) & _MASK128

    def next_uint64(self) -> int:
        self._step()
        self._draws += 1
        value = ((self._state >> 64) ^ self._state) & _MASK64
        rot = (self._state >> 122) & 63
        if rot:
            return ((value >> rot) | (value << (64 - rot))) & _MASK64
        return value

    def below(self, bound: int) -> int:
        if bound <= 0:
            raise EngineError("bound must be positive")
        limit = (1 << 64) - ((1 << 64) % bound)
        while True:
            draw = self.next_uint64()
            if draw < limit:
                return draw % bound

    def uniform(self) -> float:
        return (self.next_uint64() >> 11) * (2.0**-53)

    @property
    def draws(self) -> int:
        return self._draws


# ---------------------------------------------------------------------------
# Ring geometry.
# ---------------------------------------------------------------------------


def _add(a: Vertex, b: Vertex) -> Vertex:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a: Vertex, b: Vertex) -> Vertex:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def validate_ring(vertices: list[Vertex]) -> None:
    n = len(vertices)
    if n < 8 or n % 2:
        raise EngineError("ring length must be even and at least 8")
    if len(set(vertices)) != n:
        raise EngineError("ring is not self-avoiding")
    for k in range(n):
        step = _sub(vertices[(k + 1) % n], vertices[k])
        if sorted(abs(c) for c in step) != [0, 0, 1]:
            raise EngineError("ring contains a non-unit step")


def contacts(vertices: list[Vertex]) -> int:
    index_of = {v: k for k, v in enumerate(vertices)}
    n = len(vertices)
    total = 0
    for k in range(n):
        for step in _NEIGHBOUR_STEPS:
            other = index_of.get(_add(vertices[k], step))
            if other is not None and (k - other) % n not in (1, n - 1):
                total += 1
    return total


def radius_of_gyration_squared(vertices: list[Vertex]) -> float:
    n = len(vertices)
    cx = sum(v[0] for v in vertices) / n
    cy = sum(v[1] for v in vertices) / n
    cz = sum(v[2] for v in vertices) / n
    return (
        sum(
            (v[0] - cx) ** 2 + (v[1] - cy) ** 2 + (v[2] - cz) ** 2
            for v in vertices
        )
        / n
    )


# ---------------------------------------------------------------------------
# Knot certification: integer projection diagram + Fox calculus at t = -1.
# ---------------------------------------------------------------------------


def _project(v: Vertex, d: tuple[int, int, int]) -> tuple[int, int]:
    dx, dy, dz = d
    return (dy * v[0] - dx * v[1], dz * v[0] - dx * v[2])


def _edge_axis(step: Vertex) -> int:
    for axis in (0, 1, 2):
        if step[axis]:
            return axis
    raise EngineError("degenerate zero step in ring")


def _det_bareiss(matrix: list[list[int]]) -> int:
    size = len(matrix)
    if size == 0:
        return 1
    work = [row[:] for row in matrix]
    sign = 1
    prev = 1
    for k in range(size - 1):
        if work[k][k] == 0:
            swap = next((r for r in range(k + 1, size) if work[r][k] != 0), -1)
            if swap < 0:
                return 0
            work[k], work[swap] = work[swap], work[k]
            sign = -sign
        for r in range(k + 1, size):
            for c in range(k + 1, size):
                work[r][c] = (
                    work[k][k] * work[r][c] - work[k][c] * work[r][k]
                ) // prev
        prev = work[k][k]
    return sign * work[size - 1][size - 1]


def _diagram(
    vertices: list[Vertex], d: tuple[int, int, int]
) -> tuple[list[tuple[int, int, int]], int, list[int]]:
    """Ordered crossing occurrences of the regular projection along d.

    Returns (walk, crossing count, signs): the walk is (crossing id, edge
    index, is_over) in ring order; signs[cid] is +1/-1 from the cross product
    of the over and under projected edge directions. The projection must be
    regular: distinct vertices project to distinct points, every crossing is
    a strict interior intersection of both edges, no two edges overlap
    colinearly, and no crossing has a height tie. Any degeneracy raises
    CertificationAmbiguity so the caller falls through to the next frozen
    direction; degenerate contacts are never silently resolved, because a
    vertex-on-segment contact can perturb into a non-cancelling crossing
    pair.
    """
    n = len(vertices)
    points = [_project(v, d) for v in vertices]
    if len(set(points)) != n:
        raise CertificationAmbiguityError("vertex projection coincidence")
    heights = [v[0] * d[0] + v[1] * d[1] + v[2] * d[2] for v in vertices]
    dirs: list[tuple[int, int]] = []
    axes: list[int] = []
    dzs: list[int] = []
    for k in range(n):
        step = _sub(vertices[(k + 1) % n], vertices[k])
        axis = _edge_axis(step)
        axes.append(axis)
        dzs.append(d[axis] * step[axis])
        q = points[(k + 1) % n]
        dirs.append((q[0] - points[k][0], q[1] - points[k][1]))
    per_edge: list[list[tuple[int, Fraction, int]]] = [[] for _ in range(n)]
    total = 0
    for i in range(n):
        ai = dirs[i]
        for j in range(i + 1, n):
            if (j - i) % n in (1, n - 1):
                continue
            bj = dirs[j]
            denom = ai[0] * bj[1] - ai[1] * bj[0]
            wx = points[j][0] - points[i][0]
            wy = points[j][1] - points[i][1]
            sn = wx * bj[1] - wy * bj[0]
            tn = wx * ai[1] - wy * ai[0]
            if denom < 0:
                denom, sn, tn = -denom, -sn, -tn
            if denom == 0:
                # Parallel edges: degenerate only if colinear spans intersect.
                if tn == 0:
                    scale = ai[0] * ai[0] + ai[1] * ai[1]
                    lo = wx * ai[0] + wy * ai[1]
                    hi = lo + (bj[0] * ai[0] + bj[1] * ai[1])
                    if min(lo, hi) <= scale and max(lo, hi) >= 0:
                        raise CertificationAmbiguityError("colinear edge overlap")
                continue
            if 0 < sn < denom and 0 < tn < denom:
                delta = (
                    (heights[i] - heights[j]) * denom
                    + sn * dzs[i]
                    - tn * dzs[j]
                )
                if delta == 0:
                    raise CertificationAmbiguityError("crossing height tie")
                over_i = delta > 0
                per_edge[i].append(
                    (total, Fraction(sn, denom), 1 if over_i else 0)
                )
                per_edge[j].append(
                    (total, Fraction(tn, denom), 0 if over_i else 1)
                )
                total += 1
            elif 0 <= sn <= denom and 0 <= tn <= denom:
                raise CertificationAmbiguityError("boundary-touching contact")
    walk: list[tuple[int, int, int]] = []
    over_dir: dict[int, tuple[int, int]] = {}
    under_dir: dict[int, tuple[int, int]] = {}
    for i in range(n):
        per_edge[i].sort(key=lambda item: item[1])
        for cid, _, over in per_edge[i]:
            walk.append((cid, i, over))
            target = over_dir if over else under_dir
            if cid in target:
                raise EngineError("crossing occurrence bookkeeping failure")
            target[cid] = dirs[i]
    signs: list[int] = []
    for cid in range(total):
        a = over_dir[cid]
        b = under_dir[cid]
        cross = a[0] * b[1] - a[1] * b[0]
        if cross == 0:
            raise CertificationAmbiguityError("crossing sign tie")
        signs.append(1 if cross > 0 else -1)
    return walk, total, signs


def _alexander_determinant(
    vertices: list[Vertex], d: tuple[int, int, int]
) -> int:
    """|Alexander polynomial at t = -1| from the projected diagram.

    Arcs of the diagram are the segments between consecutive under-passes
    (each arc terminates at an under-pass). For each crossing with over arc O,
    under-pass incoming arc I and outgoing arc J, the Fox-calculus row of the
    Wirtinger relation specialized at t = -1 is (O: +2, I: -1, J: -1) for a
    positive crossing and (O: -2, I: +1, J: +1) for a negative one. The
    matrix is the first c-1 rows and c-1 columns; the fraction-free Bareiss
    determinant is exact over the integers.
    """
    walk, total, signs = _diagram(vertices, d)
    if total <= 1:
        return 1
    first_under = next(index for index, occ in enumerate(walk) if not occ[2])
    rotated = walk[first_under + 1 :] + walk[: first_under + 1]
    length = len(rotated)
    arc_at = [0] * length
    arc = 0
    for position, occurrence in enumerate(rotated):
        arc_at[position] = arc
        if not occurrence[2]:
            arc += 1
    if arc != total:
        raise EngineError("arc labelling failure")
    under_position: dict[int, int] = {}
    over_position: dict[int, int] = {}
    for position, (cid, _, over) in enumerate(rotated):
        if over:
            over_position[cid] = position
        else:
            under_position[cid] = position
    if len(under_position) != total or len(over_position) != total:
        raise EngineError("occurrence bookkeeping failure")
    size = total - 1
    matrix = [[0] * size for _ in range(size)]
    for cid in range(size):
        under_pos = under_position[cid]
        incoming = arc_at[under_pos]
        outgoing = arc_at[(under_pos + 1) % length]
        over_arc = arc_at[over_position[cid]]
        entries = (
            ((over_arc, 2), (incoming, -1), (outgoing, -1))
            if signs[cid] > 0
            else ((over_arc, -2), (incoming, 1), (outgoing, 1))
        )
        row: dict[int, int] = {}
        for column, value in entries:
            row[column] = row.get(column, 0) + value
        for column, value in row.items():
            if column < size:
                matrix[cid][column] += value
    return abs(_det_bareiss(matrix))


def certify(vertices: list[Vertex]) -> int:
    """|Delta(-1)| using the first projection direction without ties."""
    failures: list[EngineError] = []
    for direction in PROJECTION_DIRECTIONS:
        try:
            return _alexander_determinant(vertices, direction)
        except CertificationAmbiguityError as exc:
            failures.append(exc)
    raise EngineError(f"all projection directions ambiguous: {failures}")


def certify_current(vertices: list[Vertex]) -> int | None:
    """Runtime invariant check; None when every frozen direction is ambiguous.

    Used only where the state is known to carry the target class by
    construction: ambiguity there is a certification limitation, not a defect,
    so the caller terminates the unit gracefully. Every other error (wrong
    class aside, which callers compare against) is a genuine invariant
    violation and propagates unchanged.
    """
    for direction in PROJECTION_DIRECTIONS:
        try:
            return _alexander_determinant(vertices, direction)
        except CertificationAmbiguityError:
            continue
    return None


def certify_all_directions(vertices: list[Vertex]) -> dict[str, int]:
    result: dict[str, int] = {}
    for direction in PROJECTION_DIRECTIONS:
        result[str(direction)] = _alexander_determinant(vertices, direction)
    return result


# ---------------------------------------------------------------------------
# Seed constructors.
# ---------------------------------------------------------------------------


def _braid_closure(word: tuple[tuple[int, int], ...], strands: int) -> list[Vertex]:
    """Closed-ring embedding of a braid word as a cubic-lattice ring.

    Strand s starts at (2s, 0, 0) and lives in the column x = 2s at y = 0.
    Each generator (p, sign) crosses the strands at columns p and p+1: the
    over strand takes a bridge at y = 1 above height z0, the under strand
    takes a tunnel at y = 0 below it, both exiting above all earlier
    activity (z0 = max column height + 2), so no two vertices ever coincide.
    Closure arcs route each strand end around nested outer shells (one per
    side, staggered heights) back to the starter of its column; the shells
    and height staggering keep the arcs vertex-disjoint from the braid and
    from each other.
    """
    if strands < 2:
        raise EngineError("braid closure needs at least two strands")
    paths: list[list[Vertex]] = [[(2 * s, 0, 0)] for s in range(strands)]
    col_strand = list(range(strands))
    ztop = [0] * strands

    def rise(path: list[Vertex], x: int, z_from: int, z_to: int) -> None:
        for z in range(z_from + 1, z_to + 1):
            path.append((x, 0, z))

    for p, sign in word:
        if not 0 <= p < strands - 1:
            raise EngineError("braid generator out of range")
        left, right = col_strand[p], col_strand[p + 1]
        x_left, x_right = 2 * p, 2 * p + 2
        z0 = max(ztop[p], ztop[p + 1]) + 2
        tunnel_x = x_left + 1
        if sign > 0:
            # Left strand over: bridge at y = 1; right strand under: tunnel.
            over, under = paths[left], paths[right]
            rise(over, x_left, paths[left][-1][2], z0 - 1)
            over.extend(
                [
                    (x_left, 1, z0 - 1),
                    (x_left, 1, z0),
                    (x_left + 1, 1, z0),
                    (x_right, 1, z0),
                    (x_right, 0, z0),
                    (x_right, 0, z0 + 1),
                    (x_right, 0, z0 + 2),
                ]
            )
            rise(under, x_right, paths[right][-1][2], z0 - 1)
            under.extend(
                [
                    (tunnel_x, 0, z0 - 1),
                    (tunnel_x, 0, z0),
                    (tunnel_x, 0, z0 + 1),
                    (tunnel_x, 0, z0 + 2),
                    (x_left, 0, z0 + 2),
                ]
            )
            rise(under, x_left, z0 + 2, z0 + 3)
        else:
            over, under = paths[right], paths[left]
            rise(over, x_right, paths[right][-1][2], z0 - 1)
            over.extend(
                [
                    (x_right, 1, z0 - 1),
                    (x_right, 1, z0),
                    (x_right - 1, 1, z0),
                    (x_left, 1, z0),
                    (x_left, 0, z0),
                    (x_left, 0, z0 + 1),
                    (x_left, 0, z0 + 2),
                ]
            )
            rise(under, x_left, paths[left][-1][2], z0 - 1)
            under.extend(
                [
                    (tunnel_x, 0, z0 - 1),
                    (tunnel_x, 0, z0),
                    (tunnel_x, 0, z0 + 1),
                    (tunnel_x, 0, z0 + 2),
                    (x_right, 0, z0 + 2),
                ]
            )
            rise(under, x_right, z0 + 2, z0 + 3)
        col_strand[p], col_strand[p + 1] = col_strand[p + 1], col_strand[p]
        ztop[p], ztop[p + 1] = z0 + 3, z0 + 2
        if sign < 0:
            ztop[p], ztop[p + 1] = z0 + 2, z0 + 3

    end_column = {col_strand[c]: c for c in range(strands)}
    global_top = max(ztop)

    def closure_arc(column: int) -> list[Vertex]:
        left_side = column < (strands + 1) // 2
        rank = column if left_side else strands - 1 - column
        shell = -3 - 2 * rank if left_side else 2 * (strands - 1) + 3 + 2 * rank
        top = global_top + 4 + 4 * rank
        bottom = -4 - 4 * rank
        arc: list[Vertex] = []
        rise(arc, 2 * column, ztop[column], top)
        x_from = 2 * column - 1 if left_side else 2 * column + 1
        x_step = -1 if left_side else 1
        arc.extend((x, 0, top) for x in range(x_from, shell + x_step, x_step))
        arc.extend((shell, 0, z) for z in range(top - 1, bottom - 1, -1))
        arc.extend(
            (x, 0, bottom) for x in range(shell - x_step, 2 * column - x_step, -x_step)
        )
        rise(arc, 2 * column, bottom, -1)
        return arc

    arcs = {c: closure_arc(c) for c in range(strands)}
    segments: list[list[Vertex]] = []
    current = 0
    visited = set()
    while True:
        visited.add(current)
        segments.append(paths[current])
        end = end_column[current]
        segments.append(arcs[end])
        if end == 0:
            break
        current = end
    if len(visited) != strands:
        raise EngineError("braid closure has multiple components")
    vertices = [v for segment in segments for v in segment]
    validate_ring(vertices)
    return vertices


def pad_to_length(vertices: list[Vertex], target: int) -> list[Vertex]:
    """Grow the ring by local two-edge decorations, preserving N and class."""
    if target < len(vertices) or (target - len(vertices)) % 2:
        raise EngineError("padding target parity or size invalid")
    ring = list(vertices)
    occupancy = set(ring)
    scan_start = 0
    while len(ring) < target:
        placed = False
        for offset in range(len(ring)):
            k = (scan_start + offset) % len(ring)
            u = ring[k]
            v = ring[(k + 1) % len(ring)]
            edge = _sub(v, u)
            for decor in _DECORATION_ORDER:
                if decor == edge or decor == (-edge[0], -edge[1], -edge[2]):
                    continue
                p1 = _add(u, decor)
                p2 = _add(p1, edge)
                if p1 in occupancy or p2 in occupancy:
                    continue
                ring[k + 1 : k + 1] = [p1, p2]
                occupancy.add(p1)
                occupancy.add(p2)
                scan_start = (k + 3) % len(ring)
                placed = True
                break
            if placed:
                break
        if not placed:
            raise EngineError("no padding site available")
    validate_ring(ring)
    return ring


def planar_rectangle(n_vertices: int) -> list[Vertex]:
    """Perimeter-filling planar rectangle: the N-exact unknot seed."""
    if n_vertices < 8 or n_vertices % 2:
        raise EngineError("rectangle needs an even length of at least 8")
    width = max(2, n_vertices // 4)
    height = n_vertices // 2 - width
    if height < 2:
        raise EngineError("rectangle dimensions degenerate")
    vertices: list[Vertex] = [(x, 0, 0) for x in range(width + 1)]
    vertices += [(width, y, 0) for y in range(1, height + 1)]
    vertices += [(x, height, 0) for x in range(width - 1, -1, -1)]
    vertices += [(0, y, 0) for y in range(height - 1, 0, -1)]
    if len(vertices) != n_vertices:
        raise EngineError("rectangle vertex count mismatch")
    validate_ring(vertices)
    return vertices


def seed_ring(knot: str, n_vertices: int) -> list[Vertex]:
    if knot not in KNOT_DETERMINANTS:
        raise EngineError(f"unknown knot class {knot}")
    if knot == "0_1":
        ring: list[Vertex] = planar_rectangle(n_vertices)
    else:
        base = _braid_closure(_BRAID_WORDS[knot], _BRAID_STRANDS[knot])
        ring = pad_to_length(base, n_vertices)
    observed = certify(ring)
    if observed != KNOT_DETERMINANTS[knot]:
        raise EngineError(
            f"seed constructor class mismatch for {knot}: |det| = {observed}"
        )
    return ring


# ---------------------------------------------------------------------------
# Moves.
# ---------------------------------------------------------------------------

def _rotate(displacement: Vertex, axis: int, quarter: int) -> Vertex:
    x, y, z = displacement
    if axis == 0:
        if quarter == 1:
            return (x, -z, y)
        if quarter == 2:
            return (x, -y, -z)
        return (x, z, -y)
    if axis == 1:
        if quarter == 1:
            return (z, y, -x)
        if quarter == 2:
            return (-x, y, -z)
        return (-z, y, x)
    if quarter == 1:
        return (-y, x, z)
    if quarter == 2:
        return (-x, -y, z)
    return (y, -x, z)


def _corner_flip(
    rng: PCG64, vertices: list[Vertex], occupancy: set[Vertex]
) -> list[Vertex] | None:
    n = len(vertices)
    i = rng.below(n)
    a = vertices[(i - 1) % n]
    b = vertices[i]
    c = vertices[(i + 1) % n]
    ab = _sub(b, a)
    bc = _sub(c, b)
    if ab[0] * bc[0] + ab[1] * bc[1] + ab[2] * bc[2] != 0:
        return None
    flipped = (a[0] + c[0] - b[0], a[1] + c[1] - b[1], a[2] + c[2] - b[2])
    if flipped in occupancy:
        return None
    result = list(vertices)
    result[i] = flipped
    return result


def _pivot(
    rng: PCG64, vertices: list[Vertex], occupancy: set[Vertex]
) -> list[Vertex] | None:
    n = len(vertices)
    i = rng.below(n)
    j = rng.below(n)
    steps = (j - i) % n
    if steps < 2:
        return None
    quarter = 1 + rng.below(3)
    base = vertices[i]
    chord = _sub(vertices[j], base)
    nonzero = [k for k in range(3) if chord[k] != 0]
    if len(nonzero) != 1:
        return None
    axis = nonzero[0]
    interior = [(i + s) % n for s in range(1, steps)]
    kept = occupancy.difference(vertices[k] for k in interior)
    rotated: list[Vertex] = []
    for k in interior:
        point = _add(base, _rotate(_sub(vertices[k], base), axis, quarter))
        if point in kept:
            return None
        rotated.append(point)
    result = list(vertices)
    for k, point in zip(interior, rotated, strict=True):
        result[k] = point
    return result


# ---------------------------------------------------------------------------
# Proposal policy: integer family weights, optional context multipliers.
# ---------------------------------------------------------------------------


class Policy:
    """Family-selection weights with exact integer arithmetic.

    uniform: every family weight 1. table: explicit integer weights, plus an
    optional context rule multiplying family weights by bucket (integer
    multipliers selected by Rg^2 thresholds). The Hastings proposal ratio is
    computed as an exact Fraction of the (bucket-dependent) selection
    probabilities.
    """

    def __init__(self, spec: dict[str, Any]) -> None:
        kind = spec.get("kind")
        if kind == "uniform":
            weights = {family: 1 for family in FAMILIES}
            thresholds: list[float] | None = None
            multipliers: dict[str, list[int]] | None = None
        elif kind == "table":
            raw_weights = spec.get("weights")
            if not isinstance(raw_weights, dict) or set(raw_weights) != set(FAMILIES):
                raise EngineError("policy table weights must cover every family")
            weights = {}
            for family in FAMILIES:
                value = raw_weights[family]
                if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                    raise EngineError("policy weights must be non-negative integers")
                weights[family] = value
            if sum(weights.values()) == 0:
                raise EngineError("policy weights must have positive total")
            context = spec.get("context")
            if context is None:
                thresholds = None
                multipliers = None
            else:
                if not isinstance(context, dict):
                    raise EngineError("policy context must be a dict")
                if context.get("observable") != "rg2_bucket":
                    raise EngineError("unknown policy context observable")
                raw_thresholds = context.get("thresholds")
                raw_multipliers = context.get("multipliers")
                if (
                    not isinstance(raw_thresholds, list)
                    or len(raw_thresholds) != 2
                    or not all(
                        isinstance(t, (int, float))
                        and not isinstance(t, bool)
                        and math.isfinite(t)
                        for t in raw_thresholds
                    )
                    or not raw_thresholds[0] < raw_thresholds[1]
                ):
                    raise EngineError("policy context thresholds invalid")
                if not isinstance(raw_multipliers, dict) or set(raw_multipliers) != set(FAMILIES):
                    raise EngineError("policy multipliers must cover every family")
                thresholds = [float(t) for t in raw_thresholds]
                multipliers = {}
                for family in FAMILIES:
                    values = raw_multipliers[family]
                    if (
                        not isinstance(values, list)
                        or len(values) != 3
                        or not all(
                            isinstance(m, int) and not isinstance(m, bool) and m >= 0
                            for m in values
                        )
                    ):
                        raise EngineError("policy multipliers invalid")
                    multipliers[family] = list(values)
                for bucket in range(3):
                    bucket_total = sum(
                        weights[family] * multipliers[family][bucket]
                        for family in FAMILIES
                    )
                    if bucket_total <= 0:
                        raise EngineError(
                            "policy context bucket total weight must be positive"
                        )
        else:
            raise EngineError("unknown policy kind")
        self.kind = kind
        self.weights = weights
        self.thresholds = thresholds
        self.multipliers = multipliers
        self.buckets = 1 if thresholds is None else 3

    def bucket(self, rg2: float) -> int:
        if self.thresholds is None:
            return 0
        if rg2 < self.thresholds[0]:
            return 0
        if rg2 < self.thresholds[1]:
            return 1
        return 2

    def weight(self, family: str, bucket: int) -> int:
        value = self.weights[family]
        if self.multipliers is not None:
            value *= self.multipliers[family][bucket]
        return value

    def total(self, bucket: int) -> int:
        return sum(self.weight(family, bucket) for family in FAMILIES)

    def draw_family(self, rng: PCG64, bucket: int) -> str:
        total = self.total(bucket)
        pick = rng.below(total)
        for family in FAMILIES:
            pick -= self.weight(family, bucket)
            if pick < 0:
                return family
        raise EngineError("family draw arithmetic failure")

    def ratio(self, family: str, bucket_x: int, bucket_y: int) -> Fraction:
        """q(y -> x) / q(x -> y) for proposing family f from x (bucket_x)."""
        numerator = self.weight(family, bucket_y) * self.total(bucket_x)
        denominator = self.weight(family, bucket_x) * self.total(bucket_y)
        if denominator == 0:
            raise EngineError("policy ratio with zero proposal weight")
        return Fraction(numerator, denominator)


# ---------------------------------------------------------------------------
# Unit execution.
# ---------------------------------------------------------------------------

_TAU_SAMPLE_CAP = 2000


def _integral_time(series: list[float]) -> float | None:
    """Initial-positive-sequence integrated autocorrelation time estimate."""
    n = len(series)
    if n < 8:
        return None
    series = series[:_TAU_SAMPLE_CAP]
    n = len(series)
    mean = sum(series) / n
    centred = [value - mean for value in series]
    gamma0 = sum(value * value for value in centred) / n
    if gamma0 <= 0.0:
        return 0.5
    tau = 0.5
    for lag in range(1, n - 1):
        gamma = (
            sum(centred[k] * centred[k + lag] for k in range(n - lag)) / n
        )
        if gamma <= 0.0:
            break
        tau += gamma / gamma0
    return tau


def _canonical_digest(obj: Any) -> str:
    payload = json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def validate_config(config: dict[str, Any]) -> None:
    if not isinstance(config, dict):
        raise EngineError("config must be a JSON object")
    expected = {
        "branch_id",
        "epistemic_class",
        "unit_id",
        "mode",
        "system",
        "ensemble",
        "policy",
        "budget",
    }
    if set(config) != expected:
        raise EngineError(f"config keys must be exactly {sorted(expected)}")
    if not isinstance(config["branch_id"], str) or not config["branch_id"]:
        raise EngineError("branch_id must be a non-empty string")
    if config["epistemic_class"] != "sandbox_exploratory_tainted":
        raise EngineError("epistemic_class is frozen for exploration units")
    unit_id = config["unit_id"]
    if not isinstance(unit_id, str) or not unit_id.startswith("g42_"):
        raise EngineError("unit_id must be a g42_ string")
    if config["mode"] != "normal":
        raise EngineError("engine mode is frozen to normal")
    system = config["system"]
    if not isinstance(system, dict) or set(system) != {"n_vertices", "knot"}:
        raise EngineError("system keys invalid")
    n_vertices = system["n_vertices"]
    if (
        not isinstance(n_vertices, int)
        or isinstance(n_vertices, bool)
        or n_vertices < 16
        or n_vertices > 512
        or n_vertices % 2
    ):
        raise EngineError("n_vertices must be even in [16, 512]")
    if system["knot"] not in KNOT_DETERMINANTS:
        raise EngineError("knot class unknown")
    ensemble = config["ensemble"]
    if not isinstance(ensemble, dict) or set(ensemble) != {"temperature"}:
        raise EngineError("ensemble keys invalid")
    temperature = ensemble["temperature"]
    if (
        not isinstance(temperature, (int, float))
        or isinstance(temperature, bool)
        or not math.isfinite(temperature)
        or not 0.0 < temperature <= 10.0
    ):
        raise EngineError("temperature must be in (0, 10]")
    if not isinstance(config["policy"], dict):
        raise EngineError("policy must be an object")
    Policy(config["policy"])
    budget = config["budget"]
    if not isinstance(budget, dict) or set(budget) != {
        "proposals",
        "cpu_seconds",
        "thin",
    }:
        raise EngineError("budget keys invalid")
    if (
        not isinstance(budget["proposals"], int)
        or isinstance(budget["proposals"], bool)
        or not 1 <= budget["proposals"] <= 10_000_000
    ):
        raise EngineError("proposal budget out of range")
    if (
        not isinstance(budget["cpu_seconds"], (int, float))
        or isinstance(budget["cpu_seconds"], bool)
        or not math.isfinite(budget["cpu_seconds"])
        or not 0.0 < budget["cpu_seconds"] <= 14_400.0
    ):
        raise EngineError("cpu budget out of range")
    if (
        not isinstance(budget["thin"], int)
        or isinstance(budget["thin"], bool)
        or budget["thin"] < 1
    ):
        raise EngineError("thin must be a positive integer")


def run_unit(config: dict[str, Any]) -> dict[str, Any]:
    validate_config(config)
    unit_id = config["unit_id"]
    initstate = int.from_bytes(
        hashlib.sha256(unit_id.encode("utf-8")).digest()[:16], "big"
    )
    rng = PCG64(initstate, INITSEQ_EXPLORATION)
    knot = config["system"]["knot"]
    n = config["system"]["n_vertices"]
    target_det = KNOT_DETERMINANTS[knot]
    vertices = seed_ring(knot, n)
    occupancy = set(vertices)
    beta = 1.0 / config["ensemble"]["temperature"]
    policy = Policy(config["policy"])
    max_proposals = config["budget"]["proposals"]
    cpu_deadline = time.process_time() + config["budget"]["cpu_seconds"]
    thin = config["budget"]["thin"]

    proposed = {family: 0 for family in FAMILIES}
    accepted = {family: 0 for family in FAMILIES}
    invalid = {family: 0 for family in FAMILIES}
    class_rejected = 0
    energy_rejected = 0
    ambiguity_rejected = 0
    corner_checks = 0
    series_rg2: list[float] = []
    series_energy: list[float] = []
    energy = -contacts(vertices)

    def bucket_of(state: list[Vertex]) -> int:
        return policy.bucket(radius_of_gyration_squared(state))

    completed_reason = "proposal_budget"
    step = 0
    while step < max_proposals:
        if step % 64 == 0 and time.process_time() > cpu_deadline:
            completed_reason = "cpu_budget"
            break
        step += 1
        bucket_x = bucket_of(vertices)
        family = policy.draw_family(rng, bucket_x)
        proposed[family] += 1
        if family == "self_loop":
            accepted["self_loop"] += 1
        else:
            if family == "corner":
                candidate = _corner_flip(rng, vertices, occupancy)
            else:
                candidate = _pivot(rng, vertices, occupancy)
            if candidate is None:
                invalid[family] += 1
            else:
                if family == "pivot":
                    candidate_det = certify_current(candidate)
                    if candidate_det is None:
                        ambiguity_rejected += 1
                        candidate = None
                    elif candidate_det != target_det:
                        class_rejected += 1
                        candidate = None
                if candidate is not None:
                    new_energy = -contacts(candidate)
                    bucket_y = bucket_of(candidate)
                    ratio = policy.ratio(family, bucket_x, bucket_y)
                    try:
                        acceptance = min(
                            1.0,
                            math.exp(-beta * (new_energy - energy)) * float(ratio),
                        )
                    except OverflowError:
                        # the product exceeds max float, hence exceeds 1
                        acceptance = 1.0
                    if rng.uniform() < acceptance:
                        vertices = candidate
                        occupancy = set(vertices)
                        energy = new_energy
                        accepted[family] += 1
                        if family == "corner" and accepted["corner"] % 64 == 0:
                            corner_checks += 1
                            observed_det = certify_current(vertices)
                            if observed_det is None:
                                completed_reason = "certification_ambiguous"
                                break
                            if observed_det != target_det:
                                raise EngineError(
                                    "corner-flip class invariant violated"
                                )
                    else:
                        energy_rejected += 1
        if step % thin == 0:
            series_rg2.append(radius_of_gyration_squared(vertices))
            series_energy.append(energy)

    final_det = certify_current(vertices)
    if final_det is not None and final_det != target_det:
        raise EngineError("final conformation class mismatch")
    if final_det is None:
        completed_reason = "certification_ambiguous"
    validate_ring(vertices)
    tail_series = series_rg2[len(series_rg2) // 2 :]
    tau = _integral_time(series_rg2)
    tau_tail = _integral_time(tail_series)
    samples = len(series_rg2)
    rg2_mean = sum(series_rg2) / samples if samples else 0.0
    rg2_var = (
        sum((value - rg2_mean) ** 2 for value in series_rg2) / (samples - 1)
        if samples > 1
        else 0.0
    )
    tail_samples = len(tail_series)
    tail_mean = sum(tail_series) / tail_samples if tail_samples else 0.0
    rg2_var_tail = (
        sum((value - tail_mean) ** 2 for value in tail_series) / (tail_samples - 1)
        if tail_samples > 1
        else 0.0
    )
    energy_mean = sum(series_energy) / samples if samples else 0.0
    ess = samples / (2.0 * tau) if tau and samples else None
    ess_tail = (
        tail_samples / (2.0 * tau_tail) if tau_tail and tail_samples else None
    )
    return {
        "engine_version": ENGINE_VERSION,
        "branch_id": config["branch_id"],
        "unit_id": unit_id,
        "epistemic_class": config["epistemic_class"],
        "mode": "normal",
        "system": {"n_vertices": n, "knot": knot},
        "ensemble": {"temperature": config["ensemble"]["temperature"]},
        "policy": config["policy"],
        "config_digest": _canonical_digest(config),
        "randomness": {
            "initseq_exploration": hex(INITSEQ_EXPLORATION),
            "initstate_digest": hashlib.sha256(
                initstate.to_bytes(16, "big")
            ).hexdigest(),
            "uint64_draws": rng.draws,
        },
        "proposals": {
            "executed": step,
            "proposed": proposed,
            "accepted": accepted,
            "invalid": invalid,
            "class_rejected": class_rejected,
            "energy_rejected": energy_rejected,
            "ambiguity_rejected": ambiguity_rejected,
        },
        "samples": {
            "count": samples,
            "rg2_mean": rg2_mean,
            "rg2_var": rg2_var,
            "rg2_tau_int": tau,
            "rg2_ess": ess,
            "rg2_var_tail": rg2_var_tail,
            "rg2_tau_int_tail": tau_tail,
            "rg2_ess_tail": ess_tail,
            "energy_mean": energy_mean,
            "contacts_mean": -energy_mean,
        },
        "final": {
            "determinant": final_det,
            "contacts": -energy,
            "self_avoiding": True,
        },
        "corner_certification_checks": corner_checks,
        "completed_reason": completed_reason,
        "timing": {"cpu_seconds": time.process_time()},
    }
