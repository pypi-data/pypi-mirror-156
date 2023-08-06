/*
Copyright 2019-2022 Matthieu Dien and Martin Pépin
Distributed under the license GNU GPL v3 or later
See LICENSE.txt for more informations
*/

#include "cpp_simulator.hpp"
#include "cpp_xoshiro.hpp"
#include <cmath>
#include <iostream>
#include <stack>
#include <stdexcept>
#include <vector>

/* Grammar constructors *********************************************/

void CRule::set_ref_rule(CRule *rule) { this->_as_ref.rule = rule; }

CRule *make_ref(CRule *rule, double weight) {
  CRule *ref = new CRule(weight, rule_type::REF);
  ref->_as_ref.rule = rule;
  return ref;
}

CRule *make_atom(double weight) {
  CRule *atom = new CRule(weight, rule_type::ATOM);
  return atom;
}

CRule *make_epsilon() {
  CRule *epsilon = new CRule(1., rule_type::EPSILON);
  return epsilon;
}

CRule *make_marker(int id, double weight) {
  CRule *marker = new CRule(weight, rule_type::MARKER);
  marker->_as_marker.id = id;
  return marker;
}

CRule *make_union(std::vector<CRule *> &args) {
  CRule *union_rule = new CRule(0., rule_type::UNION);
  new (&union_rule->_as_n_op) std::vector<int>;
  for (auto &arg : args) {
    union_rule->weight = union_rule->weight + arg->weight;
    union_rule->_as_n_op.args.push_back(arg);
  }
  return union_rule;
}

CRule *make_product(std::vector<CRule *> &args) {
  CRule *product_rule = new CRule(1., rule_type::PRODUCT);
  new (&product_rule->_as_n_op) std::vector<int>;
  for (auto &arg : args) {
    product_rule->weight = product_rule->weight * arg->weight;
    product_rule->_as_n_op.args.push_back(arg);
  }
  return product_rule;
}

CRule *make_seq(CRule *arg, int lower_size, int upper_size) {
  const double pseudo_inverse = 1. / (1. - arg->weight);
  CRule *seq_rule = new CRule(pseudo_inverse, rule_type::SEQ);
  seq_rule->_as_iterated_rule.arg = arg;
  seq_rule->_as_iterated_rule.upper_size = -1;
  seq_rule->_as_iterated_rule.lower_size = 0;

  if (lower_size > 0) {
    seq_rule->_as_iterated_rule.lower_size = lower_size;
    seq_rule->weight *= std::pow(arg->weight, lower_size);
  }

  if (upper_size > 0) {
    seq_rule->_as_iterated_rule.upper_size = upper_size;
    seq_rule->weight -=
        pseudo_inverse * std::pow(arg->weight, (upper_size + 1));
  }

  return seq_rule;
}

CRule *make_set(CRule *arg, int lower_size, int upper_size) {
  CRule *set_rule = new CRule(0., rule_type::SET);
  set_rule->_as_iterated_rule.arg = arg;
  set_rule->_as_iterated_rule.upper_size = upper_size;
  set_rule->_as_iterated_rule.lower_size = lower_size;

  if (upper_size > 0)
    for (int i = lower_size; i <= upper_size; i++)
      set_rule->weight += std::pow(arg->weight, i) / std::tgamma(i + 1);
  else {
    set_rule->weight = std::exp(arg->weight);
    for (int i = 0; i < lower_size; i++)
      set_rule->weight -= std::pow(arg->weight, i) / std::tgamma(i + 1);
  }
  return set_rule;
}

int bnd_geometric(double param, int lower_bound, int upper_bound) {
  const double r = rand_double();
  int bounding_term = 0;
  lower_bound = lower_bound < 0 ? 0 : lower_bound;

  if (upper_bound > 0) {
    const int k = upper_bound - lower_bound;
    bounding_term = (1 - r) * std::pow(1 - param, (k + 1));
  }

  double geom = std::floor(std::log(r + bounding_term) / std::log(1 - param));
  return static_cast<int>(geom) + lower_bound;
}

int bnd_poisson(double total_weight, double param, int lower_bound,
                int upper_bound) {
  const double r = rand_double() * total_weight;
  double s = 0;
  int i = lower_bound > 0 ? lower_bound : 0;

  while (s < r) {
    s = s + std::pow(param, i) / std::tgamma(i + 1);
    i++;
  }

  if (upper_bound > 0 && i > upper_bound + 1) // XXX. Why?
    return bnd_poisson(total_weight, param, lower_bound, upper_bound);
  else
    return (i - 1);
}

void show_rule(CRule *rule) {
  std::cout << std::flush;
  std::cout << "[" << rule->weight << "] ";
  switch (rule->type) {
  case EPSILON:
    std::cout << "eps";
    break;
  case ATOM: {
    std::cout << "z";
  } break;
  case MARKER: {
    int id = rule->_as_marker.id;
    std::cout << "u" << id;
  } break;
  case REF: {
    std::cout << "REF[" << rule->_as_ref.rule << "]";
  } break;
  case UNION: {
    std::cout << "(";
    auto arg = rule->_as_n_op.args.begin();
    show_rule(*arg);
    arg++;
    while (arg != rule->_as_n_op.args.end()) {
      std::cout << " + ";
      show_rule(*arg);
      arg++;
    }
    std::cout << ")";
  } break;
  case PRODUCT: {
    std::cout << "(";
    auto arg = rule->_as_n_op.args.begin();
    show_rule(*arg);
    arg++;
    while (arg != rule->_as_n_op.args.end()) {
      std::cout << " * ";
      show_rule(*arg);
      arg++;
    }
    std::cout << ")";
  } break;
  case SET: {
    auto r = rule->_as_iterated_rule;
    std::cout << "SET(";
    show_rule(r.arg);
    std::cout << ", lower_size=" << r.lower_size;
    std::cout << ", upper_size=" << r.upper_size;
    std::cout << ")";
  } break;
  case SEQ: {
    auto r = rule->_as_iterated_rule;
    std::cout << "SEQ(";
    show_rule(r.arg);
    std::cout << ", lower_size=" << r.lower_size;
    std::cout << ", upper_size=" << r.upper_size;
    std::cout << ")";
  } break;
  default:
    throw std::invalid_argument("There is a problem with your grammar."
                                "Please report it to the developpers.");
  }
}

std::vector<int> c_simulate(CRule *first_rule, std::vector<int> &max_sizes) {
  std::vector<int> sizes(max_sizes.size());
  std::stack<CRule *> todo;

  todo.push(first_rule);
  double r = 0;

  while (!todo.empty()) {
    CRule *rule = todo.top();
    todo.pop();

    switch (rule->type) {
    case EPSILON:
      break;
    case ATOM: {
      sizes[0]++;
      if (max_sizes[0] > 0 && sizes[0] > max_sizes[0])
        return sizes;
    } break;
    case MARKER: {
      int id = rule->_as_marker.id;
      sizes[id]++;
      if (max_sizes[id] > 0 && sizes[id] > max_sizes[id])
        return sizes;
    } break;
    case REF: {
      todo.push(rule->_as_ref.rule);
    } break;
    case UNION: {
      r = rand_double() * rule->weight;
      for (auto &arg : rule->_as_n_op.args) {
        r = r - arg->weight;
        if (r <= 0) {
          todo.push(arg);
          break;
        }
      }
    } break;
    case PRODUCT: {
      for (auto &arg : rule->_as_n_op.args)
        todo.push(arg);
    } break;
    case SEQ: {
      const int k = bnd_geometric(1 - rule->_as_iterated_rule.arg->weight,
                                  rule->_as_iterated_rule.lower_size,
                                  rule->_as_iterated_rule.upper_size);
      for (int i = 0; i < k; i++)
        todo.push(rule->_as_iterated_rule.arg);
    } break;
    case SET: {
      const int k =
          bnd_poisson(rule->weight, rule->_as_iterated_rule.arg->weight,
                      rule->_as_iterated_rule.lower_size,
                      rule->_as_iterated_rule.upper_size);
      for (int i = 0; i < k; i++)
        todo.push(rule->_as_iterated_rule.arg);
    } break;
    default:
      throw std::invalid_argument("There is a problem with your grammar."
                                  "Please report it to the developpers.");
    }
  }

  return sizes;
}

// bool in_window(std::vector<int>& sizes,
//                 std::vector<int>& min_sizes,
//                 std::vector<int>& max_sizes){
//   for(auto i = 0; i < sizes.size(); i++)
//     if(sizes[i] < min_sizes[i] || sizes[i] > max_sizes[i])
//       return false;
//   return true;
// }

// std::vector<int>&& rand_perm(int n){
//   int i, j;
//   std::vector<int> p;

//   for(int i = 1; i <= n; i++)
//     p->push_back(i);

//   for(int i = n-1; i>0; i--){
//     j = rand_i64(i);
//     std::swap(*p[i], *p[j]);
//   }

//   return std::move(p);
// }

// std::vector<int> c_search_seed(Rule* first_rule,
//                               std::vector<int>& min_sizes,
//                               std::vector<int>& max_sizes,
//                               bool labelling){
//   xhoshiro::randstate backup_state;
//   get_state(backup_state);
//   std::vector<int> sizes = simulate(first_rule, max_sizes);

//   while(!in_window(sizes, min_sizes, max_sizes)){
//     // save the random generator's state
//     get_state(backup_state);
//     sizes = simulate(first_rule, max_sizes);
//   }
//   // Generate the labels BEFORE reseting the RNG
//   std::vector<int> labels;
//   if(labelling)
//     labels = rand_perm(sizes[0]);

//   // Reset the random generator to the state it was just before the
//   simulation xoshiro.set_state(backup_state); return labels;
// }
