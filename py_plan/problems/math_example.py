from operator import ne

from py_search.utils import compare_searches
from py_search.uninformed import depth_first_search
from py_search.uninformed import breadth_first_search
from py_search.uninformed import iterative_deepening_search

from py_plan.total_order import StateSpacePlanningProblem
from py_plan.base import Operator
from operator import add


add_op = Operator('add',
                  [('Number', '?n1'),
                   ('Number', '?n2')],
                  [('Number', (add, '?n1', '?n2'))])

if __name__ == "__main__":

    start = [('Number', 1)]

    goal = [('Number', 5)]

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

    p = StateSpacePlanningProblem(start, goal, [add_op])

    # print(next(best_first_search(p)).state)

    compare_searches([p], [progression,
                           regression, bidirectional,
                           iterative_deepening_search
                           ])
