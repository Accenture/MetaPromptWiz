from typing import Callable, TypeVar, Any, List

from pydantic import BaseModel

from meta_config_wiz.logger import logger
from meta_config_wiz.program_runner.program_runner import ProgramRunner

InputType = TypeVar("InputType", bound=Any)
OutputType = TypeVar("OutputType", bound=Any)

from meta_config_wiz.models.scores import EvaluationScore, ConfigurationScore


class AllMeanProgramRunner(ProgramRunner):
    """
    run all data sample in dataset, get the score for each, and return the mean of all scores
    """

    def run(self, config: BaseModel, program: Callable, dataset: list[tuple[InputType, OutputType]], scoring_function: Callable[[OutputType, OutputType], float]) -> float:
        logger.info({"config": config.model_dump()})
        scores: List[ConfigurationScore] = ProgramRunner.run_program_async(config=config, program=program, dataset=dataset, scoring_function=scoring_function)   # this will be the type of scores, assuming we use a single feature_distribution
        mean_score = sum(scores, 0.0) / len(scores)
        logger.info({"score": mean_score})
        return mean_score
