from operator import ge
from operator import sub
from functools import partial

from py_search.utils import compare_searches
from py_search.uninformed import depth_first_search

from py_plan.total_order import StateSpacePlanningProblem
from py_plan.base import Operator

buy = Operator('buy',
               [('Book', '?b'),
                ('Cost', '?b', '?c'),
                ('Money', '?m'),
                (ge, '?m', '?c')],
               [('Own', '?b'),
                ('not', ('Money', '?m')),
                ('Money', (sub, '?m', '?c'))])

start = [('Money', 30)]
for i in range(30):
    book = "book%s" % i
    start += [('Book', book), ('Cost', book, 10)]

goal = [('Own', 'book2')]

p = StateSpacePlanningProblem(start, goal, [buy])


def progression(problem):
    return partial(depth_first_search, forward=True, backward=False)(problem)


def regression(problem):
    return partial(depth_first_search, forward=False, backward=True)(problem)

def bidirectional(problem):
    return partial(depth_first_search, forward=True, backward=True)(problem)


compare_searches([p], [progression,
                       regression,
                       bidirectional
                       ])
