# Copyright 2021 AIPlan4EU project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
This module defines the Variable class.
A Variable has a name and a type.
"""


from typing import List, Set
from unified_planning.model.fnode import FNode
from unified_planning.model.operators import OperatorKind
import unified_planning
import unified_planning.walkers as walkers
import unified_planning.model.operators as op



class Variable:
    """Represents a varible."""
    def __init__(self, name: str, typename: 'unified_planning.model.types.Type'):
        self._name = name
        self._typename = typename

    def __repr__(self) -> str:
        return f'{str(self.type)} {self.name}'

    def __eq__(self, oth: object) -> bool:
        if isinstance(oth, Variable):
            return self._name == oth._name and self._typename == oth._typename
        else:
            return False

    def __hash__(self) -> int:
        return hash(self._name) + hash(self._typename)

    @property
    def name(self) -> str:
        """Returns the variable name."""
        return self._name

    @property
    def type(self) -> 'unified_planning.model.types.Type':
        """Returns the variable type."""
        return self._typename

class FreeVarsOracle(walkers.DagWalker):
    # We have only few categories for this walker.
    #
    # - Quantifiers need to exclude bounded variables
    # - Other operators need to return the union of all their sons
    # - Constants have no impact

    def get_free_variables(self, expression: FNode) -> Set[Variable]:
        """Returns the set of Symbols appearing free in the expression."""
        return self.walk(expression)

    @walkers.handles(OperatorKind.VARIABLE_EXP)
    def walk_variable_exp(self, expression: FNode, args: List[Set[Variable]], **kwargs) -> Set[Variable]:
        #pylint: disable=unused-argument
        return {expression.variable()}

    @walkers.handles(OperatorKind.EXISTS, OperatorKind.FORALL)
    def walk_quantifier(self, expression: FNode, args: List[Set[Variable]], **kwargs) -> Set[Variable]:
        #pylint: disable=unused-argument
        return args[0].difference(expression.variables())

    @walkers.handles(op.CONSTANTS)
    def walk_constant(self, expression: FNode, args: List[Set[Variable]], **kwargs) -> Set[Variable]:
        #pylint: disable=unused-argument
        return set()

    @walkers.handles(set(OperatorKind) - {OperatorKind.VARIABLE_EXP, OperatorKind.EXISTS, OperatorKind.FORALL})
    def walk_all(self, expression: FNode, args: List[Set[Variable]], **kwargs) -> Set[Variable]:
        return {v for s in args for v in s}
