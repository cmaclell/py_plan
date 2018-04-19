from py_plan.unification import unify
from py_plan.unification import subst


def test_subst():
    assert (subst({'?x': 42, '?y': 0}, ('+', ('F', '?x'), '?y')) ==
            ('+', ('F', 42), 0))

    # can use substitute to do the reverse, which is useful for variablizing
    # functions
    assert (subst({('on', 'A', 'B'): '?x'}, ('on', 'A', 'B')) == '?x')


def test_term_unification():
    # Base Terms
    assert unify('A', 'B') is None
    assert unify('A', 'A') == {}

    # Relations
    assert unify(('on', 'A'), ('on', 'B')) is None
    assert unify(('on', 'A'), ('on', 'A')) == {}
    assert unify(('on', 'A'), ('on', '?x')) == {'?x': 'A'}
    assert unify(('on', 'A'), ('?rel', 'A')) == {'?rel': 'on'}
    assert unify(('on', 'A'), ('?rel', '?x')) == {'?rel': 'on', '?x': 'A'}
    assert unify(('on', '?x'), ('?rel', 'B')) == {'?rel': 'on', '?x': 'B'}
    assert unify(('on', '?x'), ('?rel', 'B')) == {'?rel': 'on', '?x': 'B'}

    # Functions and negation will be handled in pattern matcher.
    # # Add Functions
    # assert unify((add, 3, 2), (add, '?x', 2)) == {'?x': 3}
    # assert unify((add, 3, 2), '?x') == {'?x': (add, 3, 2)}
    # assert (unify(('on', 5, '?x'),
    #               ('on', '?x', 5)) == {'?x': 5})
    # assert unify((add, 3, 2), 5) == {}
    # assert (unify(('on', (add, 3, 2), '?x'),
    #               ('on', '?y', (add, 1, 4))) ==
    #         {'?x': (add, 1, 4),
    #          '?y': (add, 3, 2)})

    # # Trouble cases.
    # assert (unify(('on', (add, 3, 2), '?x'),
    #               ('on', '?x', (add, 1, 4))) == {'?x': (add, 3, 2)})
    # assert unify((add, 3, 2), (add, 1, 4)) == {}
    # assert unify(('on', (add, 3, 2)), ('on', 5)) == {}
    # assert unify((add, '?x', 2), 5) is None
    # assert unify((add, 'A', '?x'), 'A?x') is None
    # assert unify((add, 'A', 'B'), 'AB') == {}
