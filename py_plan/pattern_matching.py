from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from itertools import product
from random import random
from random import shuffle

# from concept_formation.utils import isNumber
from py_search.base import Problem
from py_search.base import Node
from py_search.uninformed import depth_first_search
from py_plan.unification import is_variable
from py_plan.unification import subst
from py_plan.unification import unify
from py_plan.unification import execute_functions


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

    # Removed special indexing for numbers.
    # >>> index_key((('X',('Position','Block1')), 10))
    # (('X', ('Position', 'Block1')), '#NUM')

    >>> index_key((('value', ('Add', ('value', '?x'),
    ...                              ('value', '?y'))), '5'))
    (('value', ('Add', ('value', '?'), ('value', '?'))), '5')
    """
    if isinstance(fact, tuple):
        return tuple(index_key(ele) for ele in fact)
    elif is_variable(fact):
        return '?'
    # TODO pushing the near number checking into the functions
    # elif isNumber(fact):
    #     return '#NUM'
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


def get_functional_terms(term):
    """
    Traverses through a term and pulls out all the functional elements, this is
    used to extract the variables that must be bound before the function can be
    evaluated.
    """
    if isinstance(term, tuple) and len(term) > 0:
        if callable(term[0]):
            return [term]
        return [fterm for ele in term for fterm in get_functional_terms(ele)]
    return []


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


def update_fun_pattern(fun_pattern, sub, index):
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


def update_pos_pattern(pos_pattern, sub, index):
    new_pos_pattern = []

    for term in pos_pattern:
        bterm = subst(sub, term)
        key = index_key(bterm)

        if key not in index:
            return None

        if bterm not in index[key]:
            new_pos_pattern.append(term)

    return new_pos_pattern


def update_neg_pattern(neg_pattern, sub, index, free_vars=None):
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
                    if unify(bterm, fact, sub, index):
                        return None
        else:
            new_neg_pattern.append(term)

    return new_neg_pattern


def update_terms(terms, f_terms, sub, index, partial=False):
    new_terms = {}

    for necessary in terms:
        # if necessary.issubset(sub):
        if meets_requirements(necessary, sub):
            for term in terms[necessary]:
                bterm = subst(sub, term)
                if term in f_terms:
                    bterm = execute_functions(bterm)
                    if is_negated_term(bterm):
                        if bterm is False:
                            continue
                        if bterm is True:
                            return None
                    else:
                        if bterm is False:
                            return None
                        if bterm is True:
                            continue

                if is_negated_term(bterm):
                    key = index_key(bterm[1])

                    if key in index and len(index[key]) > 0:
                        for fact in index[key]:
                            if unify(bterm[1], fact, sub, index):
                                # if partial:
                                #     continue
                                return None
                else:
                    key = index_key(bterm)

                    if key not in index:
                        if partial:
                            continue
                        return None

                    if bterm not in index[key]:
                        if necessary not in new_terms:
                            new_terms[necessary] = []
                        new_terms[necessary].append(term)
        else:
            new_terms[necessary] = terms[necessary]

    return new_terms


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
        yield dict(solution.state_node.state)


def identify_determined_vars(term):
    if isinstance(term, tuple) and len(term) > 0:
        if term[0] == 'not' or callable(term[0]):
            return set()
        return set.union(*[identify_determined_vars(ele)
                           for ele in term[1:]])
    elif is_variable(term):
        return set([term])
    else:
        return set()


def identify_necessary_vars(term, determined_vars, neg=False, fun=False):
    """
    >>> det = {'?b', '?other', '?other2', '?y'}
    >>> identify_necessary_vars(('not', ('on', '?other', '?b')), det)
    {'?other', '?b'}
    """
    # print(term, determined_vars, neg, fun)

    if isinstance(term, tuple) and len(term) > 0:
        if term[0] == 'not':
            return identify_necessary_vars(term[1], determined_vars, neg=True,
                                           fun=fun)
        if callable(term[0]):
            return set.union(*[identify_necessary_vars(ele, determined_vars,
                                                       neg, fun=True)
                               for ele in term[1:]])
        return set.union(*[identify_necessary_vars(ele, determined_vars, neg,
                                                   fun)
                           for ele in term[1:]])

    if not is_variable(term):
        return set()

    if fun and term not in determined_vars:
        # print(term, determined_vars, neg, fun)
        raise Exception("Functionals cannot have existentially "
                        "quantified variables.")

    if fun or (neg and term in determined_vars):
        return set([term])

    return set()


def pattern_match(pattern, index, substitution=None, partial=False):
    """
    Find substitutions that yield a match of the pattern against the provided
    index. If no match is found then it returns None.
    """
    if substitution is None:
        substitution = {}

    sub = frozenset(substitution.items())

    determined_vars = set(v for t in pattern
                          for v in identify_determined_vars(t))
    # print('DETERMINED', determined_vars)

    terms = {}
    for t in pattern:
        necessary = frozenset(identify_necessary_vars(t, determined_vars))
        if necessary not in terms:
            terms[necessary] = []
        terms[necessary].append(t)

    # print(terms)

    f_terms = set(t for t in pattern if is_functional_term(t))

    terms = update_terms(terms, f_terms, substitution, index, partial)

    if terms is None:
        return

    if partial:
        problem = PartialMatchingProblem(sub, extra=(terms, f_terms, index))
    else:
        problem = PatternMatchingProblem(sub, extra=(terms, f_terms, index))

    for solution in depth_first_search(problem):
        yield dict(solution.state_node.state)


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
        terms, f_terms, index = node.extra

        # Figure out best term to match (only need to choose 1 and don't need
        # to backtrack over choice).
        p_terms = [(len(index[subst(sub, t)]) if t in index else 0,
                    len(necessary), random(), t) for necessary in terms
                   if meets_requirements(necessary, sub) for t in
                   terms[necessary] if not is_negated_term(t)]
        if len(p_terms) == 0:
            return

        p_terms.sort()
        term = p_terms[0][3]

        # TODO need to figure out how to handle positiver terms with functional

        # Pretty sure this is ok AND faster.
        key = index_key(subst(sub, term))
        # key = index_key(term)
        if key not in index:
            return

        facts = [f for f in index[key]]

        # could do something here where I pick the fact that yields
        # substitutions that are the LEAST constraining.
        # I'm not sure if it is worth the time though.
        shuffle(facts)

        for fact in facts:
            # TODO what do we do when the term contains a functional?
            new_sub = unify(term, fact, sub)
            if new_sub is None:
                continue

            new_terms = update_terms(terms, f_terms, new_sub, index)
            if new_terms is None:
                continue

            yield Node(frozenset(new_sub.items()), node, None, 0,
                       (new_terms, f_terms, index))

    def goal_test(self, node, goal):
        """
        If there are no positive patterns left to match, then we're done.
        """
        terms, _, _ = node.extra
        return not any(True for necessary in terms for t in terms[necessary]
                       if not is_negated_term(t))


def meets_requirements(necessary, sub):
    return all([not contains_variable(subst(sub, e)) for e in necessary])


def contains_variable(term):
    if is_variable(term):
        return True
    if isinstance(term, tuple) and len(term) > 0:
        return any(contains_variable(e) for e in term)
    return False


class PartialMatchingProblem(PatternMatchingProblem):
    """
    A variation of pattern matching that terminates at a complete match OR
    when there is nothing left to match.
    """
    def successors(self, node):
        """
        Successor nodes are possible next pattern elements that can be unified.
        """
        sub = dict(node.state)
        terms, f_terms, index = node.extra

        # Figure out best term to match (only need to choose 1 and don't need
        # to backtrack over choice).

        for term in [t for necessary in terms if
                     meets_requirements(necessary, sub)
                     for t in terms[necessary] if not is_negated_term(t)]:

            # Pretty sure this is ok AND faster.
            key = index_key(subst(sub, term))
            # key = index_key(term)
            if key not in index:
                return

            facts = [f for f in index[key]]
            # shuffle(facts)

            for fact in facts:
                new_sub = unify(term, fact, sub)
                if new_sub is None:
                    continue

                new_terms = update_terms(terms, f_terms, new_sub, index,
                                         partial=True)
                if new_terms is None:
                    continue

                yield Node(frozenset(new_sub.items()), node, None, 0,
                           (new_terms, f_terms, index))

    def goal_test(self, node, goal):
        """
        If there is some match, but there are no possible matches of the
        pattern left, then done
        """
        # need to replace the len(node.state) > 0, with something that works
        # for even surface predicate matches (no variable bindings necessary).
        return len(node.state) > 0


if __name__ == "__main__":

    from problems.blocksworld import not_equal

    kb = [
          ('block', 'A'),
          ('block', 'B'),
          ('block', 'C'),
          ('clear', 'A'),
          ('clear', 'B'),
          ('clear', 'C'),
          ('on', 'A', 'Table'),
          ('on', 'B', 'Table'),
          ('on', 'C', 'Table'),
          (not_equal, 'A', 'B'),
          (not_equal, 'B', 'C'),
          (not_equal, 'A', 'C'),
          ]
    q = [
         ('block', '?skolem39'),
         ('block', '?skolem40'),
         ('clear', '?skolem39'),
         ('on', '?skolem39', '?skolem40'),
         ('on', '?skolem40', 'Table')
         ]

    index = build_index(kb)

    from pprint import pprint
    for m in pattern_match(q, index, {}, partial=True):
        print('sol:')
        pprint(m)
