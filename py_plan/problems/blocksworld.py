from operator import ne

from py_search.utils import compare_searches
from py_search.uninformed import depth_first_search
from py_search.uninformed import breadth_first_search
from py_search.uninformed import iterative_deepening_search

from py_plan.total_order import StateSpacePlanningProblem
from py_plan.base import Operator


move = Operator('move',
                [('on', '?b', '?x'),
                 ('block', '?b'),
                 ('block', '?x'),
                 ('block', '?y'),
                 ('block', '?other'),
                 ('block', '?other2'),
                 ('not', ('on', '?other', '?b')),
                 ('not', ('on', '?other2', '?y')),
                 # ('clear', '?b'),
                 # ('clear', '?y'),
                 (ne, '?b', '?x'),
                 (ne, '?b', '?y'),
                 (ne, '?x', '?y')],
                [('on', '?b', '?y'),
                 # ('clear', '?x'),
                 ('not', ('on', '?b', '?x')),
                 # ('not', ('clear', '?y'))
                 ])

move_from_table = Operator('move_from_table',
                           [('on', '?b', 'Table'),
                            ('block', '?other'),
                            ('block', '?other2'),
                            ('not', ('on', '?other', '?b')),
                            ('not', ('on', '?other2', '?y')),
                            # ('clear', '?b'),
                            # ('clear', '?y'),
                            ('block', '?b'),
                            ('block', '?y'),
                            (ne, '?b', '?y')],
                           [('on', '?b', '?y'),
                            ('not', ('on', '?b', 'Table')),
                            # ('not', ('clear', '?y'))
                            ])

move_to_table = Operator('move_to_table',
                         [('on', '?b', '?x'),
                          ('block', '?b'),
                          ('block', '?x'),
                          ('block', '?other'),
                          ('not', ('on', '?other', '?b')),
                          # ('clear', '?b'),
                          (ne, '?b', '?x')],
                         [('on', '?b', 'Table'),
                          # ('clear', '?x'),
                          ('not', ('on', '?b', '?x'))])


if __name__ == "__main__":

    start = [('on', 'A', 'Table'),
             ('on', 'B', 'Table'),
             ('on', 'C', 'A'),
             ('block', 'A'),
             ('block', 'B'),
             ('block', 'C'),
             # ('clear', 'B'),
             # ('clear', 'C')
             ]

    goal = [('on', 'A', 'B'),
            ('on', 'B', 'C'),
            ('on', 'C', 'Table')]

    # start = [('on', 'A', 'Table'),
    #          ('on', 'B', 'Table'),
    #          ('on', 'C', 'Table'),
    #          ('block', 'A'),
    #          ('block', 'B'),
    #          ('block', 'C'),
    #          ('clear', 'A'),
    #          ('clear', 'B'),
    #          ('clear', 'C')]

    def progression(x):
        return breadth_first_search(x, forward=True, backward=False)

    def regression(x):
        return breadth_first_search(x, forward=False, backward=True)

    def bidirectional(x):
        return breadth_first_search(x, forward=True, backward=True)

    p = StateSpacePlanningProblem(start, goal, [move_from_table,
                                                move_to_table])

    # print(next(best_first_search(p)).state)

    compare_searches([p], [progression,
                           regression, bidirectional,
                           # iterative_deepening_search
    ])

    print(next(progression(p)).path())
    print(next(regression(p)).path())
