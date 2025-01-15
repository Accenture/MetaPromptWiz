from typing import Literal

from meta_config_wiz.program_runner.all_mean_program_runner import AllMeanProgramRunner
from meta_config_wiz.program_runner.program_runner import ProgramRunner


def program_runner_factory(program_runner_name: Literal['AllMean']) -> ProgramRunner:
    """
    Factory method for creating program runner instances
    :param program_runner_name: name of the program runner to create
    :return: instance of the program runner
    """
    match program_runner_name:
        case 'AllMean':
            return AllMeanProgramRunner()
        case _:
            raise ValueError(f"Unknown program runner name: {program_runner_name}")
