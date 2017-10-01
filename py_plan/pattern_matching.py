from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from itertools import product

from concept_formation.utils import isNumber
from unification import is_variable


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
    (('X',('Position','Block1')), '#NUM')

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


if __name__ == "__main__":

    from pprint import pprint
    pprint(index_key(('value', '?x', '5')))
    pprint([a for a in get_variablized_keys(('value', '?', '5'))])
