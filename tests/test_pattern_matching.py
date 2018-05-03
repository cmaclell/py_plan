from operator import ne
from operator import add
from py_plan.pattern_matching import pattern_match
from py_plan.pattern_matching import build_index
from pprint import pprint
from operator import add


def test_partial_match():
    kb = [
            ('Number', '5')
          ]
    q = [
         ('Number', '5'),
         # ('Number', '?y')
         ]

    print(list(pattern_match(q, build_index(kb), partial=True)))
    # assert list(pattern_match(q, build_index(kb), partial=True)) == {}
    # assert list(pattern_match(kb, build_index(q), partial=False)) == {}
    # assert next(match_effects(q, index, {})) == {}


def test_unify():
    pass
