from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from itertools import chain
from itertools import combinations
from operator import ne
from operator import eq
from operator import or_

from py_search.uninformed import depth_first_search
from py_search.uninformed import breadth_first_search
from py_search.informed import best_first_search
from py_search.base import Problem
from py_search.base import Node
from py_search.base import GoalNode
from py_search.utils import compare_searches

from py_plan.pattern_matching import build_index
from py_plan.pattern_matching import pattern_match
from py_plan.pattern_matching import is_functional_term
from py_plan.pattern_matching import is_negated_term
from py_plan.unification import execute_functions
from py_plan.unification import is_variable
from py_plan.unification import subst
from py_plan.base import gen_skolem
from py_plan.base import Operator


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


def get_vars(term):
    if isinstance(term, (tuple, list)) and len(term) > 0:
        return set.union(*[get_vars(ele) for ele in term])
    elif is_variable(term):
        return set([term])
    else:
        return set()


def or_constraints(constraints):
    if len(constraints) == 1:
        return constraints[0]
    return (or_, constraints[0], or_constraints(constraints[1:]))


def generate_regression_constraints(del_effects, goal_index):
    return [or_constraints([(ne, v, match[v]) for v in match]) for e in
            del_effects for match in pattern_match([e], goal_index, {})]


def generate_del_constraints(del_effects, positive_goals):
    # print(del_effects, list(positive_goals))
    return [or_constraints([(ne, match[v], v) for v in match]) for e in
            positive_goals for match in
            pattern_match([e], build_index(del_effects), {})]


def generate_add_constraints(add_effects, negative_goals):
    return [or_constraints([(ne, match[v], v) for v in match]) for e in
            negative_goals for match in
            pattern_match([e], build_index(add_effects), {})]


def replace_functionals(ele, sub):
    """
    Return the element with all functionals replaced,
    at the top level. Builds up sub along the way.
    """
    if ele in sub:
        return sub[ele]
    if isinstance(ele, tuple):
        new_ele = tuple(replace_functionals(e, sub) for e in ele)
        if callable(new_ele[0]):
            sub[new_ele] = gen_skolem()
            return sub[new_ele]
        return new_ele
    return ele


def replace_constants(ele, sub):
    """
    Return the element with all functionals replaced,
    at the top level. Builds up sub along the way.
    """
    if is_variable(ele):
        return ele
    if is_functional_term(ele):
        return ele
    if isinstance(ele, tuple) and ele[0] == 'not':
        return ele
    if isinstance(ele, tuple):
        new_ele = (ele[0],) + tuple(replace_constants(e, sub) for e in ele[1:])
        return new_ele
    sk = gen_skolem()
    sub[sk] = ele
    return sk


def is_constant(ele):
    return not isinstance(ele, tuple) and not is_variable(ele)


def is_var_assignment(ele):
    return (isinstance(ele, tuple) and ele[0] == eq and is_variable(ele[1]) and
            is_constant(ele[2]))


class StateSpacePlanningProblem(Problem):
    """
    A total order planning problem that can be solved with py_search.
    """
    # TODO Need to implement domain general heuristics, such as node_value.
    # TODO Can these heuristics guide which bidirectional search is exanded
    # first? Currently, we can't support heuristics with bidirectional search.

    def __init__(self, state, goals, operators):
        state = frozenset(state)
        self.operators = operators
        self.goal = GoalNode(frozenset(goals))
        self.initial = Node(state, parent=None, action=None, node_cost=0)
        achievable = set(e for o in self.operators
                         for e in o.add_effects)
        achievable.update(e for e in state)
        self.achievable = build_index(achievable)

    def successors(self, node):
        index = build_index(node.state)
        for o in self.operators:
            # TODO check that operators cannot have unbound variables in
            # effects.
            for m in pattern_match(o.conditions, index):
                dels = frozenset(execute_functions(e, m) if
                                 is_functional_term(e) else subst(m, e) for e
                                 in o.del_effects)
                adds = frozenset(execute_functions(e, m) if
                                 is_functional_term(e) else subst(m, e) for e
                                 in o.add_effects)
                new_state = node.state.difference(dels).union(adds)
                yield Node(new_state, node, (o, m), node.cost() + o.cost)

    def predecessors(self, node):
        for o in self.operators:
            # Rename variables to prevent collisions.
            # TODO figure out how to reverse this for printing plans
            o = o.standardized_copy()

            # Convert constants into equality constraints, so that goals with
            # constants can be matched in reverse.
            constant_mapping = {}
            var_state = frozenset(replace_constants(e, constant_mapping) for e
                                  in node.state)
            equality_constraints = set((eq, e, constant_mapping[e]) for e in
                                       constant_mapping)

            # Generate constraints that prevent operator inconsistency
            # prevent delete effects that match positive goals
            del_constraints = generate_del_constraints(o.del_effects,
                                                       [e for e in var_state if
                                                        not
                                                        is_functional_term(e)
                                                        and not
                                                        is_negated_term(e)])
            # prevent positive effects that produce negated goals
            add_constraints = generate_add_constraints(o.add_effects,
                                                       [e[1] for e in var_state
                                                        if not
                                                        is_functional_term(e)
                                                        and
                                                        is_negated_term(e)])

            # TODO figure out how to add any applicable constraints to var
            # state in order to prevent variables bindings that are
            # inconsistent this requires comparing the vars in the state with
            # those in the constraints and only adds constraints that have var
            # subsets.
            var_state = var_state.union(equality_constraints)

            for m in pattern_match(var_state,
                                   build_index(o.add_effects),
                                   partial=True):

                new_state = frozenset(subst(m, e) for e in var_state)
                new_state = new_state.difference(o.add_effects)
                new_state = new_state.union(o.conditions)

                cons = set(subst(m, e) for e in new_state if
                           is_functional_term(e))
                cons.update(subst(m, e) for e in del_constraints)
                cons.update(subst(m, e) for e in add_constraints)

                new_state = frozenset(e for e in new_state if not
                                      is_functional_term(e))
                # print("Constraints", cons)

                # Check equality constraints that disagree
                invalid = False
                assignment_mapping = {}
                for c in cons:
                    if is_var_assignment(c):
                        var = c[1]
                        const = c[2]

                        if var in assignment_mapping:
                            invalid = True
                            break

                        assignment_mapping[var] = const

                if invalid:
                    continue

                # substitute assignment equality constraints
                # back in, i.e., replace all var with constants.
                cons = set(subst(assignment_mapping, e) for e in cons
                           if not is_var_assignment(e))
                new_state = frozenset(subst(assignment_mapping, e)
                                      for e in new_state)

                # Check for any other functional constraints.
                # Terminate branches with false functions
                # Eliminate constraints that are satisfied
                new_cons = set()
                for c in cons:
                    try:
                        if execute_functions(c, m) is False:
                            invalid = True
                            break
                    except TypeError:
                        new_cons.add(c)

                if invalid:
                    continue

                # REACHABILITY ANALYSIS, check if there are any
                # new_state elements that cannot be generated by an
                # operator and do not exist in the state
                for e in new_state:
                    if is_negated_term(e):
                        continue
                    temp_m = {}
                    new_e = replace_constants(e, temp_m)
                    p = set((eq, e, temp_m[e]) for e in temp_m)
                    p.add(new_e)
                    try:
                        next(pattern_match(p, self.achievable,
                                           partial=True))
                    except Exception:
                        invalid = True
                        break

                if invalid:
                    continue

                # Add any surviving constraints back into the state
                new_state = new_state.union(new_cons)

                yield GoalNode(new_state, node, (o, m), node.cost() + o.cost)

    def goal_test(self, node, goal):
        index = build_index(node.state)
        for m in pattern_match(goal.state, index, {}):
            for v in m:
                goal.action[1][v] = m[v]
            return True
        return False


if __name__ == "__main__":

    import operator

    pickup = Operator('pickup', [('clear', '?x'), ('on', '?x', 'table'),
                                 ('hand-empty')],
                      [('not', ('on', '?x', 'table')),
                       ('not', ('clear', '?x')),
                       ('holding', '?x'),
                       ('not', ('hand-empty'))])

    putdown = Operator('putdown', [('holding', '?x')],
                       [('not', ('holding', '?x')), ('on', '?x', 'table'),
                        ('clear', '?x'), ('hand-empty')])

    stack = Operator('stack', [('holding', '?x'), ('clear', '?y')],
                     [('not', ('holding', '?x')), ('not', ('clear', '?y')),
                      ('on', '?x', '?y'), ('clear', '?x'), ('hand-empty')])

    unstack = Operator('unstack', [('on', '?x', '?y'), ('clear', '?x'),
                                   (operator.ne, '?y', 'table'),
                                   ('hand-empty')],
                       [('not', ('on', '?x', '?y')), ('not', ('clear', '?x')),
                        ('holding', '?x'), ('clear', '?y'),
                        ('not', ('hand-empty'))])

    successor = Operator('successor', [('number', '?x')],
                         [('number', ('S', '?x'))])

    state = [('on', 'C', 'A'), ('on', 'A', 'table'), ('on', 'B', 'table'),
             ('clear', 'B'), ('clear', 'C'), ('hand-empty')]
    # state = [('on', 'B', 'A'), ('on', 'A', 'table'), ('clear', 'B'),
    #          ('hand-empty'), ('on', 'C', 'table'), ('clear', 'C')]
    goals = [('on', 'A', 'B'), ('on', 'B', 'C')]

    p = StateSpacePlanningProblem(state, goals, [pickup, putdown, stack,
                                                 unstack])

    compare_searches([p], [depth_first_search, breadth_first_search,
                           best_first_search])
