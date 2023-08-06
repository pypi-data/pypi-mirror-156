# std
from __future__ import annotations
from abc import abstractmethod
import os
import subprocess
from typing import List, Union

# internal
from laz.utils.errors import LazValueError
from laz.utils import log
from laz.utils.types import Data, DictData, ListData
from laz.model.target import Target


class Action:
    action_types = []

    def __init__(self, target: Target, run_data: Data):
        self.target: Target = target
        self.run_data: Data = run_data

    def __init_subclass__(cls):
        if cls.__name__ != 'ShellAction':
            cls.action_types.append(cls)

    @abstractmethod
    def run(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        raise NotImplementedError

    @classmethod
    def new(cls, target: Target, run_data: Data) -> Action:
        for action_type in cls.action_types:
            if action_type.is_handler(target, run_data):
                return action_type.new(target, run_data)
        if ShellAction.is_handler(target, run_data):
            return ShellAction.new(target, run_data)
        cls.raise_value_error(target, run_data)

    @classmethod
    def raise_value_error(cls, target: Target, run_data: Data):
        log.error(f'target -> {target}')
        log.error(f'run data -> {run_data}')
        raise LazValueError(f'Given values could not be handled as a {cls.__name__}')


class ConfiguredAction(Action):

    def run(self):
        raise NotImplementedError

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        configured_actions: DictData = target.data.get('actions', {})
        if isinstance(run_data, str) and run_data in configured_actions:
            return True
        else:
            return False

    @classmethod
    def new(cls, target: Target, run_data: Data) -> Action:
        configured_actions: DictData = target.data.get('actions', {})
        if isinstance(run_data, str) and run_data in configured_actions:
            return Action.new(target, configured_actions[run_data])
        else:
            cls.raise_value_error(target, run_data)


class MultipleActions(Action):

    def __init__(self, target: Target, run_data: ListData):
        super().__init__(target, run_data)
        self.actions = [Action.new(target, d) for d in self.run_data]

    def run(self):
        for action in self.actions:
            action.run()

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, list)

    @classmethod
    def new(cls, target: Target, run_data: ListData) -> Action:
        return MultipleActions(target, run_data)


class ShellAction(Action):

    def run(self):
        env = {
            **os.environ,
            **self.target.data.get('env', {}),
        }
        subprocess.run(self.args(), env=env)

    def args(self) -> List[str]:
        args = self.run_data if isinstance(self.run_data, str) else ' '.join(self.run_data)
        return [self._shell(), '-c', args]

    def _shell(self) -> str:
        return os.environ.get('SHELL', 'bash')

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        if isinstance(run_data, str):
            return True
        elif isinstance(run_data, list) and all(isinstance(x, str) for x in run_data):
            return True
        else:
            cls.raise_value_error(target, run_data)

    @classmethod
    def new(cls, target: Target, run_data: Union[str, List[str]]) -> Action:
        return cls(target, run_data)


class PythonAction(Action):

    def run(self):
        eval(self.run_data['python'])

    @classmethod
    def is_handler(cls, target: Target, run_data: Data) -> bool:
        return isinstance(run_data, dict) and 'python' in run_data

    @classmethod
    def new(cls, target: Target, run_data: DictData) -> Action:
        return cls(target, run_data)
