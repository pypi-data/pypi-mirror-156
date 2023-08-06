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


import importlib
import sys
import inspect
import unified_planning as up
from unified_planning.environment import Environment
from unified_planning.model import ProblemKind
from unified_planning.plans import PlanKind
from unified_planning.engines.mixins.oneshot_planner import OptimalityGuarantee
from unified_planning.engines.mixins.compiler import CompilationKind, CompilerMixin
from unified_planning.engines.mixins.oneshot_planner import OneshotPlannerMixin
from unified_planning.engines.mixins.plan_validator import PlanValidatorMixin
from typing import IO, Dict, Tuple, Optional, List, Union, Type, cast


DEFAULT_ENGINES = {
    'fast-downward' : ('up_fast_downward', 'FastDownwardPDDLPlanner'),
    'fast-downward-opt' : ('up_fast_downward', 'FastDownwardOptimalPDDLPlanner'),
    'pyperplan' : ('up_pyperplan.engine', 'EngineImpl'),
    'enhsp' : ('up_enhsp.enhsp_planner', 'ENHSPSatEngine'),
    'enhsp-opt' : ('up_enhsp.enhsp_planner', 'ENHSPOptEngine'),
    'tamer' : ('up_tamer.engine', 'EngineImpl'),
    'sequential_plan_validator' : ('unified_planning.engines.plan_validator', 'SequentialPlanValidator'),
    'sequential_simulator' : ('unified_planning.engines.sequential_simulator', 'SequentialSimulator'),
    'up_conditional_effects_remover' : ('unified_planning.engines.compilers.conditional_effects_remover', 'ConditionalEffectsRemover'),
    'up_disjunctive_conditions_remover' : ('unified_planning.engines.compilers.disjunctive_conditions_remover', 'DisjunctiveConditionsRemover'),
    'up_negative_conditions_remover' : ('unified_planning.engines.compilers.negative_conditions_remover', 'NegativeConditionsRemover'),
    'up_quantifiers_remover' : ('unified_planning.engines.compilers.quantifiers_remover', 'QuantifiersRemover'),
    'tarski_grounder' : ('unified_planning.engines.compilers.tarski_grounder', 'TarskiGrounder'),
    'up_grounder' : ('unified_planning.engines.compilers.grounder', 'Grounder')
}


def format_table(header: List[str], rows: List[List[str]]) -> str:
    row_template = '|'
    for i in range(len(header)):
        l = max(len(r[i]) for r in [header] + rows)
        row_template += f' {{:<{str(l)}}} |'
    header_str = row_template.format(*header)
    row_len = len(header_str)
    rows_str = [f'{"-"*row_len}', f'{header_str}', f'{"="*row_len}']
    for row in rows:
        rows_str.append(f'{row_template.format(*row)}')
        rows_str.append(f'{"-"*row_len}')
    return '\n'.join(rows_str)


class Factory:
    def __init__(self, env: 'Environment', engines: Dict[str, Tuple[str, str]] = DEFAULT_ENGINES):
        self._env = env
        self.engines: Dict[str, Type['up.engines.engine.Engine']] = {}
        self._credit_disclaimer_printed = False
        for name, (module_name, class_name) in engines.items():
            try:
                self.add_engine(name, module_name, class_name)
            except ImportError:
                pass

    def add_engine(self, name: str, module_name: str, class_name: str):
        module = importlib.import_module(module_name)
        EngineImpl = getattr(module, class_name)
        self.engines[name] = EngineImpl

    def _get_engine_class(self, engine_kind: str, name: Optional[str] = None,
                          problem_kind: ProblemKind = ProblemKind(),
                          optimality_guarantee: Optional['OptimalityGuarantee'] = None,
                          compilation_kind: Optional['CompilationKind'] = None,
                          plan_kind: Optional['PlanKind'] = None) -> Type['up.engines.engine.Engine']:
        if name is not None:
            if name in self.engines:
                return self.engines[name]
            else:
                raise up.exceptions.UPNoRequestedEngineAvailableException
        problem_features = list(problem_kind.features)
        planners_features = []
        for name, EngineClass in self.engines.items():
            # Make sure that optimality guarantees and compilation kind are mutually exclusive
            assert optimality_guarantee is None or compilation_kind is None
            if getattr(EngineClass, 'is_'+engine_kind)():
                assert optimality_guarantee is None or issubclass(EngineClass, OneshotPlannerMixin)
                assert compilation_kind is None or issubclass(EngineClass, CompilerMixin)
                assert plan_kind is None or issubclass(EngineClass, PlanValidatorMixin)
                if (EngineClass.supports(problem_kind)
                    and (optimality_guarantee is None or cast(OneshotPlannerMixin, EngineClass).satisfies(optimality_guarantee))
                    and (compilation_kind is None or cast(CompilerMixin, EngineClass).supports_compilation(compilation_kind))
                    and (plan_kind is None or cast(PlanValidatorMixin, EngineClass).supports_plan(plan_kind))):
                    return EngineClass
                elif ((compilation_kind is None or cast(CompilerMixin, EngineClass).supports_compilation(compilation_kind))
                      and (plan_kind is None or cast(PlanValidatorMixin, EngineClass).supports_plan(plan_kind))):
                    x = [name] + [str(EngineClass.supports(ProblemKind({f}))) for f in problem_features]
                    if optimality_guarantee is not None:
                        x.append(str(cast(Type[OneshotPlannerMixin], EngineClass).satisfies(optimality_guarantee)))
                    planners_features.append(x)
        if len(planners_features) > 0:
            header = ['Engine'] + problem_features
            if optimality_guarantee is not None:
                header.append('OPTIMALITY_GUARANTEE')
                msg = f'No available engine supports all the problem features:\n{format_table(header, planners_features)}'
        elif compilation_kind is not None:
            msg = f'No available engine supports {compilation_kind}'
        elif plan_kind is not None:
            msg = f'No available engine supports {plan_kind}'
        else:
            msg = f'No available {engine_kind} engine'
        raise up.exceptions.UPNoSuitableEngineAvailableException(msg)

    def _print_credits(self, all_credits: List[Optional['up.engines.Credits']]):
        '''
        This function prints the credits of the engine(s) used by an operation mode
        '''
        credits: List['up.engines.Credits'] = [c for c in all_credits if c is not None]
        if len(credits) == 0:
            return

        stack = inspect.stack()
        fname = stack[3].filename
        if 'unified_planning/shortcuts.py' in fname:
            fname = stack[4].filename
            operation_mode_name = stack[3].function
            line = stack[4].lineno
        else:
            operation_mode_name = stack[2].function
            line = stack[3].lineno

        class PaleWriter(up.AnyBaseClass):
            def __init__(self, stream: IO[str]):
                self._stream = stream

            def write(self, txt:str):
                self._stream.write('\033[96m')
                self._stream.write(txt)
                self._stream.write('\033[0m')

        if self.environment.credits_stream is not None:
            w = PaleWriter(self.environment.credits_stream)

            if not self._credit_disclaimer_printed:
                self._credit_disclaimer_printed = True
                w.write(f'\033[1mNOTE: To disable printing of planning engine credits, add this line to your code: `up.shortcuts.get_env().credits_stream = None`\n')
            w.write('  *** Credits ***\n')
            w.write(f'  * In operation mode `{operation_mode_name}` at line {line} of `{fname}`, ')
            if len(credits) > 1:
                w.write('you are using a parallel planning engine with the following components:\n')
            else:
                w.write('you are using the following planning engine:\n')
            for c in credits:
                c.write_credits(w)
            w.write('\n')

    def _get_engine(self, engine_kind: str, name: Optional[str] = None,
                    names: Optional[List[str]] = None,
                    params: Union[Dict[str, str], List[Dict[str, str]]] = None,
                    problem_kind: ProblemKind = ProblemKind(),
                    optimality_guarantee: Optional['OptimalityGuarantee'] = None,
                    compilation_kind: Optional['CompilationKind'] = None,
                    plan_kind: Optional['PlanKind'] = None,
                    problem: Optional['up.model.AbstractProblem'] = None) -> 'up.engines.engine.Engine':
        if names is not None:
            assert name is None
            assert problem is None, 'Parallel simulation is not supported'
            if params is None:
                params = [{} for i in range(len(names))]
            assert isinstance(params, List) and len(names) == len(params)
            engines = []
            all_credits = []
            for name, param in zip(names, params):
                EngineClass = self._get_engine_class(engine_kind, name)
                all_credits.append(EngineClass.get_credits(**param))
                engines.append((EngineClass, param))
            self._print_credits(all_credits)
            p_engine = up.engines.parallel.Parallel(engines)
            return p_engine
        else:
            if params is None:
                params = {}
            assert isinstance(params, Dict)
            EngineClass = self._get_engine_class(engine_kind, name, problem_kind, optimality_guarantee, compilation_kind, plan_kind)
            credits = EngineClass.get_credits(**params)
            self._print_credits([credits])
            if problem is None:
                assert engine_kind != 'simulator'
                return EngineClass(**params)
            else:
                assert engine_kind == 'simulator'
                assert issubclass(EngineClass, up.engines.engine.Engine)
                assert issubclass(EngineClass, up.engines.mixins.simulator.SimulatorMixin)
                return EngineClass(problem, **params)

    @property
    def environment(self) -> 'Environment':
        '''Returns the environment in which this factory is created'''
        return self._env

    def OneshotPlanner(self, *, name: Optional[str] = None,
                       names: Optional[List[str]] = None,
                       params: Union[Dict[str, str], List[Dict[str, str]]] = None,
                       problem_kind: ProblemKind = ProblemKind(),
                       optimality_guarantee: Optional[Union['OptimalityGuarantee', str]] = None) -> 'up.engines.engine.Engine':
        """
        Returns a oneshot planner. There are three ways to call this method:
        - using 'name' (the name of a specific planner) and 'params' (planner dependent options).
          e.g. OneshotPlanner(name='tamer', params={'heuristic': 'hadd'})
        - using 'names' (list of specific planners name) and 'params' (list of
          planners dependent options) to get a Parallel engine.
          e.g. OneshotPlanner(names=['tamer', 'tamer'],
                              params=[{'heuristic': 'hadd'}, {'heuristic': 'hmax'}])
        - using 'problem_kind' and 'optimality_guarantee'.
          e.g. OneshotPlanner(problem_kind=problem.kind, optimality_guarantee=SOLVED_OPTIMALLY)
        """
        if isinstance(optimality_guarantee, str):
            optimality_guarantee = OptimalityGuarantee[optimality_guarantee]
        return self._get_engine('oneshot_planner', name, names, params, problem_kind, optimality_guarantee)

    def PlanValidator(self, *, name: Optional[str] = None,
                      names: Optional[List[str]] = None,
                      params: Union[Dict[str, str], List[Dict[str, str]]] = None,
                      problem_kind: ProblemKind = ProblemKind(),
                      plan_kind: Optional[Union['PlanKind', str]] = None) -> 'up.engines.engine.Engine':
        """
        Returns a plan validator. There are three ways to call this method:
        - using 'name' (the name of a specific plan validator) and 'params'
          (plan validator dependent options).
          e.g. PlanValidator(name='tamer', params={'opt': 'val'})
        - using 'names' (list of specific plan validators name) and 'params' (list of
          plan validators dependent options) to get a Parallel engine.
          e.g. PlanValidator(names=['tamer', 'tamer'],
                             params=[{'opt1': 'val1'}, {'opt2': 'val2'}])
        - using 'problem_kind' and 'plan_kind' parameters.
          e.g. PlanValidator(problem_kind=problem.kind, plan_kind=plan.kind)
        """
        if isinstance(plan_kind, str):
            plan_kind = PlanKind[plan_kind]
        return self._get_engine('plan_validator', name, names, params, problem_kind,
                                plan_kind=plan_kind)

    def Compiler(self, *, name: Optional[str] = None,
                 params: Union[Dict[str, str], List[Dict[str, str]]] = None,
                 problem_kind: ProblemKind = ProblemKind(),
                 compilation_kind: Optional[Union['CompilationKind', str]] = None) -> 'up.engines.engine.Engine':
        """
        Returns a Compiler. There are two ways to call this method:
        - using 'name' (the name of a specific grounder) and 'params'
          (grounder dependent options).
          e.g. Compiler(name='tamer', params={'opt': 'val'})
        - using 'problem_kind' and 'compilation_kind' parameters.
          e.g. Compiler(problem_kind=problem.kind, compilation_kind=GROUNDER)
        """
        if isinstance(compilation_kind, str):
            compilation_kind = CompilationKind[compilation_kind]
        return self._get_engine('compiler', name, None, params, problem_kind,
                                compilation_kind=compilation_kind)

    def Simulator(self,
                 problem: 'up.model.AbstractProblem', *, name: Optional[str] = None,
                 params: Union[Dict[str, str], List[Dict[str, str]]] = None) -> 'up.engines.engine.Engine':
        """
        Returns a Simulator. There are two ways to call this method:
        - using 'problem_kind' through the problem field.
          e.g. Simulator(problem)
        - using 'name' (the name of a specific simulator) and eventually some 'params'
          (simulator dependent options).
          e.g. Simulator(problem, name='sequential_simulator')
        """
        return self._get_engine('simulator', name, None, params, problem.kind,
                                problem = problem)

    def print_engines_info(self, stream: IO[str] = sys.stdout, full_credits: bool = True):
        stream.write('These are the engines currently available:\n')
        for Engine in self.engines.values():
            credits = Engine.get_credits()
            if credits is not None:
                stream.write('---------------------------------------\n')
                credits.write_credits(stream, full_credits)
                stream.write(f'This engine supports the following features:\n{str(Engine.supported_kind())}\n\n')
