# distutils: language = c++
# cython: language_level = 3

# Copyright 2019-2022 Matthieu Dien and Martin Pépin
# Distributed under the license GNU GPL v3 or later
# See LICENSE.txt for more informations

from libc.stdint cimport int64_t, uint64_t
from libcpp.map cimport map as cpp_map
from libcpp.vector cimport vector

from usainboltz.cpp_simulator cimport CRule


cpdef int bounded_geometric(double, int, int);
cpdef int bounded_poisson(double, double, int, int);

cdef class Simulator:
    cdef cpp_map[int, CRule*] c_rules
    cdef dict mapping
    cdef void grammar_to_c_struct(self, object, dict)
    cpdef list run(self, object, list)
    cdef CRule* rule_to_c_struct(self, object)

# Xoshiro stuff
cpdef void rng_seed(uint64_t)
cpdef double rng_double()
cpdef int64_t rng_i64(int64_t)
cdef void rng_get_state(uint64_t dest[4])
cdef void rng_set_state(const uint64_t s[4])
