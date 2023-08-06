# Copyright 2019-2022 Matthieu Dien and Martin Pépin
# Distributed under the license GNU GPL v3 or later
# See LICENSE.txt for more informations

"""RNA secondary structures"""

from typing import List, TextIO, Tuple

from usainboltz import (
    Atom,
    Epsilon,
    Generator,
    Grammar,
    Marker,
    RuleName,
    union_builder,
)
from usainboltz.generator import rng_seed

z = Atom()
A, U, C, G = Marker("A"), Marker("U"), Marker("C"), Marker("G")
S, Sp, B = RuleName("S"), RuleName("Sp"), RuleName("B")


grammar = Grammar(
    {
        S: B * z * Sp + B * z * S * z * Sp,
        Sp: S + Epsilon(),
        B: A + U + C + G,
    }
)
generator = Generator(grammar, S)


def dual(base: str) -> str:
    if base == "A":
        return "U"
    if base == "U":
        return "A"
    if base == "C":
        return "G"
    if base == "G":
        return "C"


def identity(x):
    return x


# ---
# RNA secondary structures as sequences of bases with offsets
# ---


# The Python type of sequences of bases.
SEQ = List[Tuple[str, int]]


def build_seq_prefix(t: Tuple[str, str, SEQ]) -> SEQ:
    base, _, s = t
    return [(base, 0)] + s


def build_seq_matching(t: Tuple[str, str, SEQ, str, SEQ]) -> SEQ:
    base, _, s, _, sp = t
    offset = len(s) + 1
    return [(base, offset)] + s + [(dual(base), -offset)] + sp


def build_seq_empty(_: str) -> SEQ:
    return []


build_seq_S = union_builder(build_seq_prefix, build_seq_matching)
build_seq_Sp = union_builder(identity, build_seq_empty)


# ---
# RNA secondary structures as forests
# ---


class Counter:
    def __init__(self):
        self.n = 0

    def next(self) -> int:
        r = self.n
        self.n += 1
        return r


# the type of forests
FOREST = List["Tree"]


def forest_str(f: FOREST) -> str:
    return "[{}]".format(", ".join(map(str, f)))


def forest_dot(f: FOREST, counter: Counter, file: TextIO) -> List[int]:
    return [tree.dot(counter, file) for tree in f]


class Tree:
    def __init__(self, children: FOREST):
        self.children = children

    def dot(self, counter, file) -> int:
        my_id = counter.next()
        children_ids = forest_dot(self.children, counter, file)
        file.write(f'  {my_id} ["shape"="point"]\n')
        for child_id in children_ids:
            file.write(f"  {my_id} -> {child_id}\n")
        return my_id

    def __str__(self):
        return f"Tree({forest_str(self.children)})"


def build_forest_prefix(t: Tuple[str, str, FOREST]) -> FOREST:
    _, _, s = t
    return s


def build_forest_matching(t: Tuple[str, str, FOREST, str, FOREST]) -> FOREST:
    _, _, s, _, sp = t
    return [Tree(s)] + sp


def build_forest_empty(_) -> FOREST:
    return []


build_forest_S = union_builder(build_forest_prefix, build_forest_matching)
build_forest_Sp = union_builder(identity, build_forest_empty)


# ---
# The order to RNA secondary structures
# ---


def order_prefix(t):
    _, _, s = t
    return s


def order_matching(t):
    _, _, s, _, sp = t
    order_s, _ = s
    order_sp, flag_sp = sp
    if order_s < order_sp:
        return sp
    if order_s > order_sp:
        return (order_s, True)
    if flag_sp:
        return (order_sp + 1, False)
    else:
        return (order_sp, True)


def order_empty(_):
    return (1, False)


order_S = union_builder(order_prefix, order_matching)
order_Sp = union_builder(identity, order_empty)


if __name__ == "__main__":
    SEED = 0x8FFF2FAD00DC576B
    SIZE = 20

    print(f"=> Using seed: 0x{SEED:x}")

    print("=> Grammar:")
    print(grammar)

    print("=> Using the default builders:")
    rng_seed(SEED)
    res = generator.sample((SIZE, SIZE))
    print(res.obj)

    print("=> Using the sequence builders:")
    generator.set_builder(S, build_seq_S)
    generator.set_builder(Sp, build_seq_Sp)
    rng_seed(SEED)
    res = generator.sample((SIZE, SIZE))
    print(res.obj)

    print("=> Using the forest builders:")
    generator.set_builder(S, build_forest_S)
    generator.set_builder(Sp, build_forest_Sp)
    rng_seed(SEED)
    res = generator.sample((SIZE, SIZE))
    print(forest_str(res.obj))
    with open("forest.dot", "w") as file:
        file.write("digraph G {\n")
        forest_dot(res.obj, Counter(), file)
        file.write("}\n")

    print("=> Using the order builders:")
    generator.set_builder(S, order_S)
    generator.set_builder(Sp, order_Sp)
    rng_seed(SEED)
    res = generator.sample((SIZE, SIZE))
    print(res.obj)
