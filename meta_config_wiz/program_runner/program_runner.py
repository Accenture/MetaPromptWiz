from abc import ABC, abstractmethod
from typing import Callable, TypeVar, Generic, Any

from pydantic import BaseModel
import asyncio

InputType = TypeVar("InputType", bound=Any)
OutputType = TypeVar("OutputType", bound=Any)

from meta_config_wiz.models.scores import EvaluationScore


class ProgramRunner(ABC, Generic[InputType, OutputType]):
    """
    Given a configuration, a program, a dataset, and a scoring function, return the list of scores for the program for each data sample in the dataset
    :param config: Configuration
    """

    @staticmethod
    def run_program_async(config: BaseModel, program: Callable, dataset: list[tuple[InputType, OutputType]], scoring_function: Callable[[OutputType, OutputType], EvaluationScore]) -> list[EvaluationScore]:
        """ return list of scores for each data sample in the dataset, computed asynchronously """

        async def run_program_async(input: InputType, expected_result: OutputType):
            result_pred: OutputType = await asyncio.to_thread(program, config, input)
            try:
                score: EvaluationScore = scoring_function(result_pred, expected_result)
            except TypeError:
                score: EvaluationScore = scoring_function(result_pred)
            return score

        async def run_programs_async():
            tasks = [run_program_async(input, expected_result) for input, expected_result in dataset]
            return await asyncio.gather(*tasks)

        scores = asyncio.run(run_programs_async())
        return scores

    @abstractmethod
    def run(self, config: BaseModel, program: Callable, dataset: list[tuple[InputType, OutputType]], scoring_function: Callable[[OutputType, OutputType], float]) -> float:
        pass