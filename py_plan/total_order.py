from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from py_search.uninformed import depth_first_search
from py_search.uninformed import breadth_first_search
from py_search.informed import best_first_search
from py_search.base import Problem
from py_search.base import Node
from py_search.utils import compare_searches

from py_plan.pattern_matching import build_index
from py_plan.pattern_matching import pattern_match
from py_plan.unification import subst
from py_plan.base import Operator


class ProgressionProblem(Problem):

    def __init__(self, state, goals, operators):
        initial = frozenset(state)
        extra = (goals, operators)
        self.initial = Node(initial, parent=None, action=None, node_cost=0,
                            extra=extra)

    def successors(self, node):
        index = build_index(node.state)
        _, operators = node.extra
        print()
        print('state', node.state)

        for o in operators:
            print('OPERATOR', o)
            for m in o.match(index):
                dels = frozenset(subst(m, e) for e in o.del_effects)
                adds = frozenset(subst(m, e) for e in o.add_effects)
                new_state = node.state.difference(dels).union(adds)
                print('succ', (o, m), new_state)
                yield Node(new_state, node, (o, m), node.cost() + o.cost,
                           node.extra)

    def goal_test(self, node):
        index = build_index(node.state)
        goals, _ = node.extra

        for m in pattern_match(goals, index, {}):
            return True
        return False


class RegressionProblem(Problem):

    def __init__(self, state, goals, operators):
        initial = frozenset(goals)
        extra = (state, operators)
        self.initial = Node(initial, parent=None, action=None, node_cost=0,
                            extra=extra)

    def successors(self, node):
        index = build_index(node.state)
        _, operators = node.extra
        print()
        print('goal', node.state)

        for o in operators:
            print(o.effects)
            for m in pattern_match(o.effects, index, {}, 0.0):
                dels = frozenset(subst(m, e) for e in o.add_effects)
                adds = frozenset(subst(m, e) for e in o.conditions)
                print(adds)
                goals = node.state.difference(dels).union(adds)
                
                print()
                print(o, goals)

                yield Node(goals, node, (o, m), node.cost() + o.cost,
                           node.extra)

    def goal_test(self, node):
        goals = node.state
        state, _ = node.extra
        index = build_index(state)

        for m in pattern_match(goals, index, {}):
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

    p = ProgressionProblem(state, goals, [pickup, putdown, stack,
                                                unstack])

    compare_searches([p], [depth_first_search, breadth_first_search,
                           best_first_search])
