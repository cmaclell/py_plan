from py_search.utils import compare_searches
from py_search.uninformed import depth_first_search
from py_search.informed import best_first_search

from py_plan.total_order import ProgressionProblem
from py_plan.base import Operator

def not_equal(a, b):
    return a != b

move = Operator('move',
                [('on', '?b', '?x'),
                 ('clear', '?b'),
                 ('clear', '?y'),
                 ('block', '?b'),
                 ('block', '?y'),
                 (not_equal, '?b', '?x'),
                 (not_equal, '?b', '?y'),
                 (not_equal, '?x', '?y')],
                [('on', '?b', '?y'),
                 ('clear', '?x'),
                 ('not', ('on', '?b', '?x')),
                 ('not', ('clear', '?y'))])

move_to_table = Operator('move_to_table',
                         [('on', '?b', '?x'),
                          ('clear', '?b'),
                          ('block', '?b'),
                          (not_equal, '?b', '?x')],
                         [('on', '?b', 'Table'),
                          ('clear', '?x'),
                          ('not', ('on', '?b', '?x'))])

start = [('on', 'A', 'Table'),
         ('on', 'B', 'Table'),
         ('on', 'C', 'A'),
         ('block', 'A'),
         ('block', 'B'),
         ('block', 'C'),
         ('clear', 'B'),
         ('clear', 'C')]

goal = [('on', 'A', 'B'),
        ('on', 'B', 'C')]

p = ProgressionProblem(start, goal, [move, move_to_table])
compare_searches([p], [depth_first_search, best_first_search])
