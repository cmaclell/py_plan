from __future__ import print_function
from __future__ import unicode_literals
from __future__ import absolute_import
from __future__ import division

from py_plan.pattern_matching import is_negated_term
from py_plan.pattern_matching import extract_strings
from py_plan.unification import is_variable
from py_plan.unification import subst

skolem = 0


def gen_skolem():
    global skolem
    skolem += 1
    return '?skolem%i' % skolem


class Operator:

    def __init__(self, name, conditions, effects, cost=1, reverse_sub=None):
        # make the name just a descriptive string / annotation.
        self.name = name
        self.conditions = set(conditions)
        self.effects = set(effects)
        self.cost = cost

        self.pos_cond = set()
        self.neg_cond = set()
        self.add_effects = set()
        self.del_effects = set()

        if reverse_sub is None:
            self.reverse_sub = {}
        else:
            self.reverse_sub = reverse_sub

        for c in self.conditions:
            if is_negated_term(c):
                self.pos_cond.add(c[1])
            else:
                self.neg_cond.add(c)

        pos_vars = set(s for term in self.pos_cond
                       for s in extract_strings(term)
                       if is_variable(s))
        neg_vars = set(s for term in self.neg_cond
                       for s in extract_strings(term)
                       if is_variable(s))
        self.free_vars = neg_vars - pos_vars

        for e in self.effects:
            if isinstance(e, tuple) and len(e) > 0 and e[0] == 'not':
                self.del_effects.add(e[1])
            else:
                self.add_effects.add(e)

        # TODO test to ensure no functions use free variables.
        # TODO replace any equality constraints between variables by just
        # replacing the variables.

    def standardized_copy(self):
        args = set(e for term in self.conditions.union(self.effects) for e in
                   extract_strings(term) if is_variable(e))
        sub = {a: gen_skolem() for a in args}
        reverse_sub = {sk: sub[sk] for sk in sub}

        conditions = set(subst(sub, c) for c in self.conditions)
        effects = set(subst(sub, e) for e in self.effects)

        return Operator(self.name, conditions, effects, self.cost, reverse_sub)

    def __str__(self):
        s = "Name: %s" % self.name + "\n"
        s += "Cost: %0.2f" % self.cost + "\n"
        s += "Conditions: %s" % self.conditions + "\n"
        s += "Effects: %s" % self.effects + "\n"
        return s

    def __repr__(self):
        return str(self.name)


if __name__ == "__main__":

    from py_plan.pattern_matching import build_index

    kb = [('A'), ('B'), ('C')]
    q = [('A'), ('B')]

    index = build_index(kb)

    o = Operator("test", q, [])
    print(o)
    for m in o.match(index):
        print("MATCH FOUND", m)
