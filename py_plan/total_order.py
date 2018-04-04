from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from itertools import chain
from itertools import combinations

from py_search.uninformed import depth_first_search
from py_search.uninformed import breadth_first_search
from py_search.informed import best_first_search
from py_search.base import Problem
from py_search.base import Node
from py_search.base import GoalNode
from py_search.utils import compare_searches

from py_plan.pattern_matching import build_index
from py_plan.pattern_matching import pattern_match
from py_plan.pattern_matching import is_negated_term
from py_plan.unification import subst
from py_plan.base import Operator


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))


class ProgressionProblem(Problem):

    def __init__(self, state, goals, operators):
        state = frozenset(state)
        self.operators = operators
        self.goal = GoalNode(frozenset(goals))
        self.initial = Node(state, parent=None, action=None, node_cost=0)

    def successors(self, node):
        index = build_index(node.state)
        # print()
        # print('state', node.state)

        for o in self.operators:
            # print('OPERATOR', o)
            for m in o.match(index):
                dels = frozenset(subst(m, e) for e in o.del_effects)
                adds = frozenset(subst(m, e) for e in o.add_effects)
                new_state = node.state.difference(dels).union(adds)
                # print('succ', (o, m), new_state)
                yield Node(new_state, node, (o, m), node.cost() + o.cost)

    def predecessors(self, node):
        # TODO replace negated facts with renaming, so NOTs are treated as
        # relations for the purposes of rule matching (not goal testing).
        state = frozenset(('NOT', e[1]) if is_negated_term(e) else e for e in
                          node.state)

        index = build_index(state)

        for o in self.operators:
            o = o.standardized_copy(rename_neg=True)
            # print()
            # print("--------------------")
            # print('STATE', node.state)
            # print(o)
            for sub in o.match_goals(index):
                for m in powerset(sub.items()):
                    m = dict(m)
                    # print(m)
                    rename_state = frozenset(subst(m, e) for e in node.state)
                    # print(m)
                    dels = frozenset(('not', subst(m, e)[1])
                                     if isinstance(e, tuple) and len(e) > 0 and
                                     e[0] == 'NOT'
                                     else subst(m, e) for e in o.effects)
                    adds = frozenset(('not', subst(m, e)[1])
                                     if isinstance(e, tuple) and len(e) > 0 and
                                     e[0] == 'NOT'
                                     else subst(m, e) for e in o.conditions)
                    new_state = rename_state.difference(dels).union(adds)

                    # print()
                    # print(node.state)
                    # print(new_state)

                    yield GoalNode(new_state, node, (o, m),
                                   node.cost() + o.cost)

                # if False:
                #     yield None

    def goal_test(self, node, goal):
        index = build_index(node.state)

        for m in pattern_match(goal.state, index, {}):
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
