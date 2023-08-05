# The modeling features language
# A high level language to describe model features and ranges of model features


# ; and \n separates features
# feature names are case insensitive
# FEATURE_NAME(options)     options is a comma separated list
# absorption(x)   - x can be FO, ZO, SEQ-ZO-FO, [FO, ZO] for multiple or * for all
# elimination(x)  - x can be FO, ZO, MM and MIX-FO-MM
# peripherals(n)  - n can be 0, 1, ... or a..b for a range (inclusive in both ends)
# transits(n)     - n as above


import functools
import itertools
from collections import OrderedDict
from typing import Iterable, Tuple

from lark import Lark
from lark.visitors import Interpreter

import pharmpy.modeling as modeling

grammar = r"""
start: feature (_SEPARATOR feature)*
feature: absorption | elimination | peripherals | transits | lagtime

absorption: "ABSORPTION"i "(" (option) ")"
elimination: "ELIMINATION"i "(" (option) ")"
peripherals: "PERIPHERALS"i "(" (option) ")"
transits: "TRANSITS"i "(" option ["," depot_opt] ")"
depot_opt: (DEPOT | NODEPOT | wildcard)
DEPOT: "DEPOT"
NODEPOT: "NODEPOT"
lagtime: "LAGTIME()"
option: (wildcard | range | value | array)
wildcard: "*"
range: NUMBER ".." NUMBER
value: /[a-zA-Z0-9-]+/
array: "[" [value ("," value)*] "]"
_SEPARATOR: /;|\n/
NUMBER: /\d+/
%ignore " "
"""


class ModelFeature:
    pass


class Absorption(ModelFeature):
    def __init__(self, tree):
        self.args = OneArgInterpreter('absorption', ('FO', 'ZO', 'SEQ-ZO-FO')).interpret(tree)
        self._funcs = dict()
        for arg in self.args:
            name = f'ABSORPTION({arg})'
            if arg == 'FO':
                self._funcs[name] = modeling.set_first_order_absorption
            elif arg == 'ZO':
                self._funcs[name] = modeling.set_zero_order_absorption
            elif arg == 'SEQ-ZO-FO':
                self._funcs[name] = modeling.set_seq_zo_fo_absorption
            else:
                raise ValueError(f'Absorption {arg} not supported')


class Elimination(ModelFeature):
    def __init__(self, tree):
        self.args = OneArgInterpreter('elimination', ('FO', 'ZO', 'MM', 'MIX-FO-MM')).interpret(
            tree
        )
        self._funcs = dict()
        for arg in self.args:
            name = f'ELIMINATION({arg})'
            if arg == 'FO':
                self._funcs[name] = modeling.set_first_order_elimination
            elif arg == 'ZO':
                self._funcs[name] = modeling.set_zero_order_elimination
            elif arg == 'MM':
                self._funcs[name] = modeling.set_michaelis_menten_elimination
            elif arg == 'MIX-FO-MM':
                self._funcs[name] = modeling.set_mixed_mm_fo_elimination
            else:
                raise ValueError(f'Elimination {arg} not supported')


class Transits(ModelFeature):
    def __init__(self, tree):
        interpreter = OneArgInterpreter('transits', ())
        self.args = interpreter.interpret(tree)
        depot = getattr(interpreter, 'depot_opt_value', 'DEPOT')
        if isinstance(depot, str):
            self.depot = depot
        else:
            self.depot = 'DEPOT'
        self._funcs = dict()
        for arg in self.args:
            if self.depot != 'NODEPOT':
                self._funcs[f'TRANSITS({arg})'] = functools.partial(
                    modeling.set_transit_compartments, n=arg
                )
            if self.depot != 'DEPOT':
                self._funcs[f'TRANSITS({arg}, NODEPOT)'] = functools.partial(
                    modeling.set_transit_compartments, n=arg + 1, keep_depot=False
                )


class Peripherals(ModelFeature):
    def __init__(self, tree):
        self.args = OneArgInterpreter('peripherals', ()).interpret(tree)
        self._funcs = dict()
        for arg in self.args:
            name = f'PERIPHERALS({arg})'
            self._funcs[name] = functools.partial(modeling.set_peripheral_compartments, n=arg)


class Lagtime(ModelFeature):
    def __init__(self, tree):
        self._funcs = {'LAGTIME()': modeling.add_lag_time}
        self.args = None


class OneArgInterpreter(Interpreter):
    def __init__(self, name: str, a: Tuple[str, ...]):
        self.name = name
        self.all = a

    def visit_children(self, tree):
        a = super().visit_children(tree)
        return set().union(*a)

    def interpret(self, tree):
        return self.visit_children(tree)

    def feature(self, tree):
        return self.visit_children(tree)

    def absorption(self, tree):
        if self.name == 'absorption':
            return self.visit_children(tree)
        else:
            return []

    def elimination(self, tree):
        if self.name == 'elimination':
            return self.visit_children(tree)
        else:
            return []

    def transits(self, tree):
        if self.name == 'transits':
            return self.visit_children(tree)
        else:
            return []

    def peripherals(self, tree):
        if self.name == 'peripherals':
            return self.visit_children(tree)
        else:
            return []

    def option(self, tree):
        return self.visit_children(tree)

    def depot_opt(self, tree):
        depot_opt = tree.children[0]
        if not isinstance(depot_opt, str):
            depot_opt = '*'
        self.depot_opt_value = depot_opt
        return []

    def value(self, tree):
        value = tree.children[0].value
        if self.name == 'transits' or self.name == 'peripherals':
            return {int(value)}
        else:
            return {value.upper()}

    def array(self, tree):
        return self.visit_children(tree)

    def wildcard(self, tree):
        if self.name == 'peripherals' or self.name == 'transits':
            raise ValueError(f'Wildcard (*) not supported for {self.name}')
        return set(self.all)

    def range(self, tree):
        return set(range(int(tree.children[0]), int(tree.children[1]) + 1))


class ModelFeatures:
    def __init__(self, code):
        parser = Lark(grammar)
        tree = parser.parse(code)
        self._all_features = []
        if list(tree.find_data('absorption')):
            self.absorption = Absorption(tree)
            self._all_features.append(self.absorption)
        if list(tree.find_data('elimination')):
            self.elimination = Elimination(tree)
            self._all_features.append(self.elimination)
        if list(tree.find_data('transits')):
            self.transits = Transits(tree)
            self._all_features.append(self.transits)
        if list(tree.find_data('peripherals')):
            self.peripherals = Peripherals(tree)
            self._all_features.append(self.peripherals)
        if list(tree.find_data('lagtime')):
            self.lagtime = Lagtime(tree)
            self._all_features.append(self.lagtime)

    def all_funcs(self):
        funcs = dict()
        for feat in self._all_features:
            # For absorption the order seems to be random
            feat_funcs = OrderedDict(sorted(feat._funcs.items(), key=lambda t: t[0]))
            funcs.update(feat_funcs)
        return funcs

    def next_funcs(self, have):
        funcs = dict()
        names = [s.split('(')[0].strip().upper() for s in have]
        for feat, func in self.all_funcs().items():
            curname = feat.split('(')[0].strip().upper()
            if curname not in names:
                funcs[feat] = func
        return funcs

    def all_combinations(self) -> Iterable[Tuple[str, ...]]:
        feats = []
        for feat in self._all_features:
            feats.append([None] + list(feat._funcs.keys()))
        for t in itertools.product(*feats):
            a = tuple(elt for elt in t if elt is not None)
            if a:
                yield a

    def get_funcs_same_type(self, feat):
        if hasattr(self, 'absorption') and feat in self.absorption._funcs.keys():
            funcs = self.absorption._funcs.values()
        elif hasattr(self, 'elimination') and feat in self.elimination._funcs.keys():
            funcs = self.elimination._funcs.values()
        elif hasattr(self, 'transits') and feat in self.transits._funcs.keys():
            funcs = self.transits._funcs.values()
        elif hasattr(self, 'peripherals') and feat in self.peripherals._funcs.keys():
            funcs = self.peripherals._funcs.values()
        elif hasattr(self, 'lagtime') and feat in self.lagtime._funcs.keys():
            funcs = self.lagtime._funcs.values()
        else:
            return []
        return list(funcs)
