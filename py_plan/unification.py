"""
Utilities for the py_plan library.
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from operator import or_


def execute_functions(fun, s=()):
    """
    Traverses a fact executing any functions present within. Returns a fact
    where functions are replaced with the function return value.

    >>> import operator
    >>> execute_functions((operator.eq, 5, 5))
    True
    >>> execute_functions((operator.eq, 5, 6))
    False

    """
    if s == ():
        s = {}

    if isinstance(fun, tuple) and len(fun) > 0:
        if fun[0] == or_:
            try:
                if execute_functions(fun[1], s) is not False:
                    return True
            except TypeError as e:
                if execute_functions(fun[2], s) is not False:
                    return True
                raise e
            return execute_functions(fun[2], s)

        if callable(fun[0]):
            return fun[0](*[execute_functions(ele, s) for ele in fun[1:]])
        else:
            return tuple(execute_functions(ele, s) for ele in fun)
    if fun in s:
        return execute_functions(s[fun])
    if is_variable(fun):
        raise TypeError("Variables cannot be left unbound in functions.")
    return fun


def is_variable(x):
    """
    Checks if the provided expression x is a variable, i.e., a string that
    starts with ?.

    >>> is_variable('?x')
    True
    >>> is_variable('x')
    False
    """
    return isinstance(x, str) and len(x) > 0 and x[0] == "?"


def is_function(x):
    """
    Checks if the provided expression x is a function term. i.e., a tuple
    where the first element is callable.
    """
    return isinstance(x, tuple) and len(x) > 0 and callable(x[0])


def subst(s, x):
    """
    Substitute the substitution s into the expression x.

    >>> subst({'?x': 42, '?y':0}, ('+', ('F', '?x'), '?y'))
    ('+', ('F', 42), 0)
    """
    if x in s:
        return s[x]
    elif isinstance(x, tuple):
        return tuple(subst(s, xi) for xi in x)
    else:
        return x


def unify(x, y, s=(), check=False):
    """
    Unify expressions x and y given a provided mapping (s).  By default s is
    (), which gets recognized and replaced with an empty dictionary. Return a
    mapping (a dict) that will make x and y equal or, if this is not possible,
    then it returns None.

    >>> unify(('Value', '?a', '8'), ('Value', 'cell1', '8'), {})
    {'?a': 'cell1'}

    >>> unify(('Value', '?a', '8'), ('Value', 'cell1', '?b'), {})
    {'?a': 'cell1', '?b': '8'}
    """
    if s == ():
        s = {}

    if s is None:
        return None
    if x == y:
        return s
    if is_variable(x):
        return unify_var(x, y, s, check)
    if is_variable(y):
        return unify_var(y, x, s, check)
    # if is_function(x):
    #     return unify_fun(x, y, s, check)
    # if is_function(y):
    #     return unify_fun(y, x, s, check)
    if (isinstance(x, tuple) and isinstance(y, tuple) and len(x) == len(y)):
        if not x:
            return s
        return unify(x[1:], y[1:], unify(x[0], y[0], s, check), check)
    return None


def unify_var(var, x, s, check=False):
    """
    Unify var with x using the mapping s. If check is True, then do an occurs
    check. By default the occurs check is turned off. Shutting the check off
    improves unification performance, but can sometimes result in unsound
    inference.

    >>> unify_var('?x', '?y', {})
    {'?x': '?y'}

    >>> unify_var('?x', ('relation', '?x'), {}, True)

    >>> unify_var('?x', ('relation', '?x'), {})
    {'?x': ('relation', '?x')}

    >>> unify_var('?x', ('relation', '?y'), {})
    {'?x': ('relation', '?y')}
    """
    if var in s:
        return unify(s[var], x, s, check)
    elif x in s:
        return unify(var, s[x], s, check)
    elif check and occur_check(var, x):
        return None
    else:
        return extend(s, var, x)


def unify_fun(fun, x, s, check=False):
    """
    Unify x with y using mapping s. If check is True, then do an occurs
    check. By default the occurs check is turned off. Shutting the check off
    improves unification performance, but can sometimes result in unsound
    inference.
    """
    result = None
    if (isinstance(fun, tuple) and isinstance(x, tuple) and
            len(fun) == len(x)):
        result = unify(fun[1:], x[1:], unify(fun[0], x[0], s, check), check)
    if result is None:
        try:
            result = unify(execute_functions(fun, s), x, s, check)
        except TypeError:
            pass
    return result


def occur_check(var, x):
    """
    Check if x contains var. This prevents binding a variable to an expression
    that contains the variable in an infinite loop.

    >>> occur_check('?x', '?x')
    True
    >>> occur_check('?x', '?y')
    False
    >>> occur_check('?x', ('relation', '?x'))
    True
    >>> occur_check('?x', ('relation', ('relation2', '?x')))
    True
    >>> occur_check('?x', ('relation', ('relation2', '?y')))
    False
    """
    if var == x:
        return True
    if isinstance(x, (list, tuple)):
        for e in x:
            if occur_check(var, e):
                return True
    return False


def extend(s, var, val):
    """
    Given a dictionary s and a variable and value, this returns a new dict with
    var:val added to the original dictionary.

    >>> extend({'a': 'b'}, 'c', 'd')
    {'a': 'b', 'c': 'd'}
    """
    s2 = {a: s[a] for a in s}
    s2[var] = val
    return s2


if __name__ == "__main__":

    print(unify('?x', ('relation', '?x'), {}))
