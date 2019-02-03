from operator import ne

from py_search.utils import compare_searches
from py_search.uninformed import breadth_first_search

from py_plan.total_order import StateSpacePlanningProblem
from py_plan.base import Operator

from random import seed

seed(0)

load = Operator('load',
                [('At', '?c', '?a'),
                 ('At', '?p', '?a'),
                 ('Cargo', '?c'),
                 ('Plane', '?p'),
                 ('Airport', '?a')],
                [('not', ('At', '?c', '?a')),
                 ('In', '?c', '?p')])

unload = Operator('unload',
                  [('In', '?c', '?p'),
                   ('At', '?p', '?a'),
                   ('Cargo', '?c'),
                   ('Plane', '?p'),
                   ('Airport', '?a')],
                  [('At', '?c', '?a'),
                   ('not', ('In', '?c', '?p'))])

fly = Operator('fly',
               [('At', '?p', '?from'),
                ('Plane', '?p'),
                ('Airport', '?from'),
                ('Airport', '?to'),
                (ne, '?from', '?to')],
               [('not', ('At', '?p', '?from')),
                ('At', '?p', '?to')])

start = [('At', 'C1', 'SFO'),
         ('At', 'C2', 'JFK'),
         ('At', 'P1', 'SFO'),
         ('At', 'P2', 'JFK'),
         ('Cargo', 'C1'),
         ('Cargo', 'C2'),
         ('Plane', 'P1'),
         ('Plane', 'P2'),
         ('Airport', 'JFK'),
         ('Airport', 'SFO')]

goal = [('At', 'C1', 'JFK'),
        # ('At', 'C2', 'SFO')
        ]


def progression(x):
    return breadth_first_search(x, forward=True, backward=False)


def regression(x):
    return breadth_first_search(x, forward=False, backward=True)


def bidirectional(x):
    return breadth_first_search(x, forward=True, backward=True)


p = StateSpacePlanningProblem(start, goal, [load, unload, fly])

compare_searches([p], [progression,  regression,
                       bidirectional])

print(next(progression(p)).path())
path = next(regression(p)).path()

print(path[0][0])
