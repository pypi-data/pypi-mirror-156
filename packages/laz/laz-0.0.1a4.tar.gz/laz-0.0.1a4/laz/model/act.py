# std
import os
import subprocess
from typing import List

# internal
from laz.utils.contexts import in_dir
from laz.model.action import Action
from laz.model.target import Target
from laz.utils.templates import expand


class Act:

    def __init__(self, target: Target, args: List[str]):
        target.push(expand(target.data))
        self.target = target
        self.args = expand(args, target.data)
        self.action = Action.new(self.target, ' '.join(self.args))

    def act(self):
        with in_dir(self.target.data['dirpath']):
            self.action.run()
