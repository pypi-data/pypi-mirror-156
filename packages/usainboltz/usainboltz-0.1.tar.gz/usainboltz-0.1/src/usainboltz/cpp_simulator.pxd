# cython: language_level = 3

# Copyright 2019-2022 Matthieu Dien and Martin Pépin
# Distributed under the license GNU GPL v3 or later
# See LICENSE.txt for more informations

from libc.stdint cimport int64_t, uint64_t
from libcpp.vector cimport vector


cdef extern from "cpp_simulator.cpp":
    pass

cdef extern from "cpp_xoshiro.cpp":
    pass

cdef extern from "cpp_simulator.hpp":
    cdef cppclass CRule:
        void set_ref_rule(CRule*)

    CRule* make_ref(CRule*, double)
    CRule* make_atom(double)
    CRule* make_epsilon()
    CRule* make_marker(int, double)
    CRule* make_union(vector[CRule*]& args)
    CRule* make_product(vector[CRule*]& args)
    CRule* make_seq(CRule*, int, int)
    CRule* make_set(CRule*, int, int);
    int bnd_geometric(double, int, int)
    int bnd_poisson(double, double, int, int)
    vector[int] c_simulate(CRule*, vector[int]& max_sizes) except +

cdef extern from "cpp_xoshiro.hpp":
    double rand_double()
    int64_t rand_i64(const int64_t bound)

    void seed(const uint64_t seed)
    void get_state(uint64_t dest[4])
    void set_state(const uint64_t s[4])
