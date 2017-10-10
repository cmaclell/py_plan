from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from itertools import product
from random import random
from random import shuffle

from concept_formation.utils import isNumber
from py_search.base import Problem
from py_search.base import Node
from py_search.uninformed import depth_first_search
from py_plan.unification import is_variable
from py_plan.unification import subst
from py_plan.unification import unify


def build_index(facts):
    """
    Given an iterator of facts returns a dict index.
    """
    index = {}
    for fact in facts:
        key = index_key(fact)
        # print('KEY', key)
        for k in get_variablized_keys(key):
            # print('VB KEY', k)
            if k not in index:
                index[k] = []
            index[k].append(fact)
    return index


def index_key(fact):
    """
    A new total indexing of the fact. Just build the whole damn thing, assuming
    it doesn't explode the memory usage.

    >>> index_key('cell')
    'cell'

    >>> index_key(('cell',))
    ('cell',)

    >>> index_key(('cell', '5'))
    ('cell', '5')

    >>> index_key((('value', '?x'), '5'))
    (('value', '?'), '5')

    >>> index_key((('X',('Position','Block1')), 10))
    (('X', ('Position', 'Block1')), '#NUM')

    >>> index_key((('value', ('Add', ('value', '?x'),
    ...                              ('value', '?y'))), '5'))
    (('value', ('Add', ('value', '?'), ('value', '?'))), '5')
    """
    if isinstance(fact, tuple):
        return tuple(index_key(ele) for ele in fact)
    elif is_variable(fact):
        return '?'
    elif isNumber(fact):
        return '#NUM'
    else:
        return fact


def get_variablized_keys(key):
    """
    Takes the triple key given above (fact[0], fact[1], value) and returns all
    the possible variablizations of it.

    >>> [k for k in get_variablized_keys(('value', 'cell', '5'))]
    [('value', 'cell', '5'), ('value', 'cell', '?'), \
('value', '?', '5'), ('value', '?', '?'), '?']

    >>> [k for k in get_variablized_keys(('value', '?', '5'))]
    [('value', '?', '5'), ('value', '?', '?'), '?']

    >>> [k for k in get_variablized_keys((('value',
    ...                                    ('Add', ('value', 'TableCell'),
    ...                                            ('value', 'TableCell'))),
    ...                                    '5'))]
    [(('value', ('Add', ('value', 'TableCell'), ('value', 'TableCell'))), \
'5'), (('value', ('Add', ('value', 'TableCell'), ('value', 'TableCell'))), \
'?'), (('value', ('Add', ('value', 'TableCell'), ('value', '?'))), '5'), \
(('value', ('Add', ('value', 'TableCell'), ('value', '?'))), '?'), (('value', \
('Add', ('value', 'TableCell'), '?')), '5'), (('value', ('Add', ('value', \
'TableCell'), '?')), '?'), (('value', ('Add', ('value', '?'), ('value', \
'TableCell'))), '5'), (('value', ('Add', ('value', '?'), ('value', \
'TableCell'))), '?'), (('value', ('Add', ('value', '?'), ('value', '?'))), \
'5'), (('value', ('Add', ('value', '?'), ('value', '?'))), '?'), (('value', \
('Add', ('value', '?'), '?')), '5'), (('value', ('Add', ('value', '?'), \
'?')), '?'), (('value', ('Add', '?', ('value', 'TableCell'))), '5'), ((\
'value', ('Add', '?', ('value', 'TableCell'))), '?'), (('value', ('Add', \
'?', ('value', '?'))), '5'), (('value', ('Add', '?', ('value', '?'))), '?'), \
(('value', ('Add', '?', '?')), '5'), (('value', ('Add', '?', '?')), '?'), \
(('value', '?'), '5'), (('value', '?'), '?'), ('?', '5'), ('?', '?'), '?']
    """
    yield key

    if isinstance(key, tuple):

        if isinstance(key[0], tuple):
            head = None
            body = key
        else:
            head = key[0]
            body = key[1:]

        possible_bodies = [list(get_variablized_keys(e)) for e in
                           body]
        for body in product(*possible_bodies):
            if head is None:
                new = tuple(body)
            else:
                new = (head,) + tuple(body)
            if new != key:
                yield new

    if not is_variable(key):
        yield '?'


def extract_strings(s):
    """
    Gets all of the string elements via iterator and depth first traversal.
    """
    if isinstance(s, (tuple, list)):
        for ele in s:
            for inner in extract_strings(ele):
                yield '%s' % inner
    else:
        yield s


def is_functional_term(term):
    """
    Checks if the provided element is a term and is a functional term.
    """
    if callable(term):
        return True
    elif isinstance(term, tuple) and len(term) > 0:
        for ele in term:
            if is_functional_term(ele):
                return True

    return False


def is_negated_term(term):
    """
    Checks if a provided element is a term and is a negated term.
    """
    return isinstance(term, tuple) and len(term) > 0 and term[0] == 'not'


def update_fun_pattern(fun_pattern, sub, index, epsilon):
    new_fun_pattern = []
    bound_set = set(sub)

    for term in fun_pattern:
        args = set(e for e in extract_strings(term) if is_variable(e))
        if args.issubset(bound_set):
            bterm = subst(sub, term)

            # might raise an exception, probably shouldn't happen unless there
            # is an error in the user specified function
            result = execute_functions(bterm)

            if result is True:
                continue

            if result is False:
                return None

            key = index_key(result)
            if key not in index or result not in index[key]:
                return None

        else:
            new_fun_pattern.append(term)

    return fun_pattern


def execute_functions(fact):
    """
    Traverses a fact executing any functions present within. Returns a fact
    where functions are replaced with the function return value.

    >>> import operator
    >>> execute_functions((operator.eq, 5, 5))
    True
    >>> execute_functions((operator.eq, 5, 6))
    False

    """
    if isinstance(fact, tuple) and len(fact) > 0:
        if callable(fact[0]):
            return fact[0](*[execute_functions(ele) for ele in fact[1:]])
        else:
            return tuple(execute_functions(ele) for ele in fact)

    return fact


def update_pos_pattern(pos_pattern, sub, index, epsilon):
    new_pos_pattern = []

    for term in pos_pattern:
        bterm = subst(sub, term)
        key = index_key(bterm)

        if key not in index:
            return None

        if bterm not in index[key]:
            new_pos_pattern.append(term)

    return new_pos_pattern


def update_neg_pattern(neg_pattern, sub, index, epsilon, free_vars=None):
    if free_vars is None:
        free_vars = set()

    new_neg_pattern = []
    bound_set = set(sub).union(free_vars)

    for term in neg_pattern:
        args = set(e for e in extract_strings(term) if is_variable(e))
        if args.issubset(bound_set):
            bterm = execute_functions(subst(sub, term))

            if bterm is False:
                continue
            if bterm is True:
                return None

            key = index_key(bterm)

            if key in index and len(index[key]) > 0:
                for fact in index[key]:
                    if unify(bterm, fact, sub, index, epsilon):
                        return None
        else:
            new_neg_pattern.append(term)

    return new_neg_pattern


def new_match(pos_terms, neg_terms, free_vars, index, substitution):
    substitution = frozenset(substitution.items())

    pos_terms = update_pos_pattern(pos_terms, substitution, index)
    if pos_terms is None:
        return

    neg_terms = update_neg_pattern(neg_terms, substitution, index, free_vars)
    if neg_terms is None:
        return

    problem = PatternMatchingProblem(substitution, extra=(pos_terms, neg_terms,
                                                          free_vars, index))

    for solution in depth_first_search(problem):
        yield dict(solution.state)


def pattern_match(pattern, index, substitution, epsilon=0.0):
    """
    Find substitutions that yield a match of the pattern against the provided
    index. If no match is found then it returns None.
    """
    substitution = frozenset(substitution.items())
    pos_terms = [t for t in pattern if not is_negated_term(t) and not
                 is_functional_term(t)]
    pos_args = set(s for term in pos_terms for s in extract_strings(term) if is_variable(s))

    neg_terms = [t[1] for t in pattern if is_negated_term(t)]
    neg_args = set(s for term in neg_terms for s in extract_strings(term) if is_variable(s))

    # print(pos_args, neg_args)
    unbound_args = neg_args.difference(pos_args)
    print(unbound_args)

    fun_terms = [t for t in pattern if not is_negated_term(t) and
                 is_functional_term(t)]

    neg_terms = update_neg_pattern(neg_terms, substitution, index,
                                   epsilon)
    if neg_terms is None:
        return

    fun_terms = update_fun_pattern(fun_terms, substitution, index,
                                   epsilon)
    if fun_terms is None:
        return

    pos_terms = update_pos_pattern(pos_terms, substitution, index, epsilon)
    if pos_terms is None:
        return

    problem = PatternMatchingProblem(substitution, extra=(pos_terms, neg_terms,
                                                          fun_terms, index,
                                                          epsilon))

    for solution in depth_first_search(problem):
        yield dict(solution.state)


class PatternMatchingProblem(Problem):
    """
    Used to unify a complex first-order pattern. Supports negations in
    patterns using negation-as-failure.
    """
    def successors(self, node):
        """
        Successor nodes are possible next pattern elements that can be unified.
        """
        sub = dict(node.state)
        pos_terms, neg_terms, fun_terms, index, epsilon = node.extra

        # Figure out best term to match (only need to choose 1 and don't need
        # to backtrack over choice).
        terms = [(len(index[term]) if term in index else 0, random(), term) for
                 term in pos_terms]
        terms.sort()
        term = terms[0][2]

        # Pretty sure this is ok AND faster.
        key = index_key(subst(sub, term))
        # key = index_key(term)
        if key not in index:
            return

        facts = [f for f in index[key]]
        shuffle(facts)

        for fact in facts:
            new_sub = unify(term, fact, sub, epsilon)
            if new_sub is None:
                continue

            new_neg_terms = update_neg_pattern(neg_terms, new_sub, index,
                                               epsilon)
            if new_neg_terms is None:
                continue

            new_fun_terms = update_fun_pattern(fun_terms, new_sub, index,
                                               epsilon)
            if new_fun_terms is None:
                continue

            new_pos_terms = update_pos_pattern(pos_terms, new_sub, index, epsilon)

            if new_pos_terms is None:
                continue

            yield Node(frozenset(new_sub.items()), node, None, 0,
                       (new_pos_terms, new_neg_terms, new_fun_terms, index,
                        epsilon))

    def goal_test(self, node):
        """
        If there are no positive patterns left to match, then we're done.
        """
        pos_terms, _, _, _, _ = node.extra
        return len(pos_terms) == 0


def eq(a, b):
    return a == b


if __name__ == "__main__":

    kb = [('Number', 1), ('Number', 2)]
    q = [('Number', '?x'), ('not', ('Number', '?y'))]

    index = build_index(kb)

    from pprint import pprint
    for a in pattern_match(q, index, {}):
        print('sol:')
        pprint(a)
