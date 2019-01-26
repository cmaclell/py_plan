from py_search.utils import compare_searches
from py_search.uninformed import breadth_first_search

from py_plan.total_order import StateSpacePlanningProblem
from py_plan.base import Operator

remove = Operator('remove',
                  [('at', '?obj', '?loc')],
                  [('not', ('at', '?obj', '?loc')),
                   ('at', '?obj', 'ground')])

puton = Operator('puton',
                 [('tire', '?t'),
                  ('at', '?t', 'ground'),
                  ('not', ('at', 'flat', 'axle'))],
                 [('not', ('at', '?t', 'ground')),
                  ('at', '?t', 'axle')])

leave_overnight = Operator('leave_overnight',
                           [],
                           [('not', ('at', 'spare', 'ground')),
                            ('not', ('at', 'spare', 'axle')),
                            ('not', ('at', 'spare', 'trunk')),
                            ('not', ('at', 'flat', 'ground')),
                            ('not', ('at', 'flat', 'axle')),
                            ('not', ('at', 'flat', 'trunk'))])

start = [('tire', 'flat'),
         ('tire', 'spare'),
         ('at', 'flat', 'axle'),
         ('at', 'spare', 'trunk')]

goal = [('at', 'spare', 'axle')]

p = StateSpacePlanningProblem(start, goal, [remove, puton, leave_overnight])


def progression(x):
    return breadth_first_search(x, forward=True, backward=False)


def regression(x):
    return breadth_first_search(x, forward=False, backward=True)


def bidirectional(x):
    return breadth_first_search(x, forward=True, backward=True)


compare_searches([p], [progression, regression, bidirectional])


print(next(progression(p)).path())
print(next(regression(p)).path())
