# distutils: language = c++
# cython: language_level = 3

# Copyright 2019-2022 Matthieu Dien and Martin Pépin
# Distributed under the license GNU GPL v3 or later
# See LICENSE.txt for more informations

from libcpp.map cimport map as cpp_map
from libcpp.utility cimport pair
from libcpp.vector cimport vector

from usainboltz.cpp_simulator cimport (
    CRule,
    bnd_geometric,
    bnd_poisson,
    c_simulate,
    get_state,
    make_atom,
    make_epsilon,
    make_marker,
    make_product,
    make_ref,
    make_seq,
    make_set,
    make_union,
    rand_double,
    rand_i64,
    seed,
    set_state,
)

from usainboltz.grammar import (
    Atom,
    Cycle,
    Epsilon,
    Marker,
    Product,
    RuleName,
    Seq,
    Set,
    Union,
)

# CRule* is valid syntax wherever the cython parser expects a type, but not inside
# brackets e.g. when applying C++ templates.
# To work around this issue we define an alise for CRule*
ctypedef CRule* CRule_ptr


# --- Wrapper on top of basic distributions implemented in C++ ------


cpdef int bounded_geometric(double d, int n, int m):
    return bnd_geometric(d,n,m)

cpdef int bounded_poisson(double a, double b, int c, int d):
    return bnd_poisson(a,b,c,d)


# --- Wrapper on top of the C++ simulator ---------------------------


cdef class Simulator:
    def __init__(self, grammar, weights, mapping):
        self.mapping = dict()
        self.mapping[Epsilon()] = -1
        self.mapping[Atom()] = 0

        for marker in grammar.markers():
            self.mapping[marker] = 1 + mapping.marker_to_id[marker]

        for rule_name in grammar.rules.keys():
            self.mapping[rule_name] = -2 - mapping.rule_name_to_id[rule_name]

        self.grammar_to_c_struct(grammar, weights)

    cdef void grammar_to_c_struct(self, object grammar, dict weights):
        """Conversion of a Python grammar into a C++ grammar"""

        cdef CRule* epsilon = make_epsilon()
        cdef CRule* atom = make_atom(weights[Atom()])

        self.c_rules.insert(pair[int, CRule_ptr](self.mapping[Epsilon()], epsilon))
        self.c_rules.insert(pair[int, CRule_ptr](self.mapping[Atom()], atom))

        cdef int marker_id
        cdef CRule* marker
        for m in grammar.markers():
            marker_id = self.mapping[m]
            marker = make_marker(marker_id, weights[m])
            self.c_rules.insert(pair[int, CRule_ptr](self.mapping[m], marker))

        cdef CRule* ref
        for rulename in grammar.rules:
            ref = make_ref(NULL, weights[rulename])
            self.c_rules.insert(pair[int, CRule_ptr](self.mapping[rulename], ref))

        cdef CRule* rn_rb
        for rulename, rulebody in grammar.rules.items():
            rn_rb = self.c_rules[self.mapping[rulename]]
            rn_rb.set_ref_rule(self.rule_to_c_struct(rulebody))

    cpdef list run(self, object rulename, list max_sizes):
        cdef vector[int] ms = max_sizes
        cdef CRule* start = self.c_rules[self.mapping[rulename]]
        return c_simulate(start, ms)

    cdef CRule* rule_to_c_struct(self, rule):
        cdef vector[CRule_ptr] args
        cdef CRule* c_arg
        cdef int ls, us

        if isinstance(rule, (RuleName, Atom, Marker, Epsilon)):
            return self.c_rules[self.mapping[rule]]
        elif isinstance(rule, Union):
            args.clear()
            for arg in rule.args:
                c_arg = self.rule_to_c_struct(arg)
                args.push_back(c_arg)
            return make_union(args)
        elif isinstance(rule, Product):
            args.clear()
            for arg in rule.args:
                c_arg = self.rule_to_c_struct(arg)
                args.push_back(c_arg)
            return make_product(args)
        elif isinstance(rule, Seq):
            ls = 0 if rule.lower_size is None else rule.lower_size
            us = -1 if rule.upper_size is None else rule.upper_size
            c_arg = self.rule_to_c_struct(rule.arg)
            return make_seq(c_arg, ls, us)
        elif isinstance(rule, Set):
            ls = 0 if rule.lower_size is None else rule.lower_size
            us = -1 if rule.upper_size is None else rule.upper_size
            c_arg = self.rule_to_c_struct(rule.arg)
            return make_set(c_arg, ls, us)
        else:
            raise NotImplementedError(f"Operator not {type(rule)} yet supported.")


# --- Wrapper on top of PRNG functions ------------------------------


cpdef void rng_seed(uint64_t s):
    seed(s)


cpdef double rng_double():
    return rand_double()


cpdef int64_t rng_i64(int64_t bound):
    return rand_i64(bound)


cdef void rng_get_state(uint64_t dest[4]):
    get_state(dest)


cdef void rng_set_state(const uint64_t s[4]):
    set_state(s)
