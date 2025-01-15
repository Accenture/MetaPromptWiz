from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import TypeVar, Generic
from meta_config_wiz.models.scores import EvaluationScore, ConfigurationScore
from meta_config_wiz.program_runner.program_runner import OutputType

class ConfigurationEvaluator(ABC):
    """
    Abstract class for evaluating the output of a configuration
    Takes the output of a configuration that is configuration scores, and aggregates them into a score that will be used by the strategy to compare configurations
    """
    @abstractmethod
    def __call__(self, evaluation_scores: EvaluationScore) -> ConfigurationScore:
        pass
    
class SampleEvaluator(ABC):
    """
    Takes a configuration, and initalizes an LLM application accodintly.
    Runs evaluation w.r.t. to a single sample and returns evaluation scores (e.g., accuracy, f1, cost, running_time, etc.)
    :param config: Configuration
    :return: EvaluationScore    
    """
    @abstractmethod
    def __call__(self, output: OutputType, expected_output: OutputType=None) -> EvaluationScore:
        pass


