from pydantic import BaseModel
from typing import Type, TypeVar, Generic, Callable
from abc import ABC, abstractmethod

# Any pydantic BaseModel. Defined here to enable using he same BaseModel for all strategies
ConfigType = TypeVar("ConfigType", bound=BaseModel)


class AbstractStrategy(ABC, Generic[ConfigType]):
    """
    Abstract base class for a strategy for searching configurations

    Maintainace a list of explored configurations and their result scores
    Decides which configuration to test next
    """

    def __init__(self, config_class_type: Type[ConfigType], max_runs: int = -1, **kwargs):
        self.config_class_type: Type[ConfigType] = config_class_type  # class of the configuration, used for generating new configuration instances
        self.max_runs: int = max_runs     # some of the strategies may want to use a maximum number of runs, they will have to set it using set_max_runs method
        self.configs: list[ConfigType] = []  # list of configurations
        self.scores: list[float] = []  # list of scores for each configuration

    def choose_best_config(self) -> ConfigType:
        """
        :return: highest scoring configuration
        """
        best_score: float = max(self.scores)
        return self.configs[self.scores.index(best_score)]

    @abstractmethod
    def run_strategy(self, func: Callable[[ConfigType], float], **kwargs) -> None:
        """
        Runs a startegy to search the configuration space 
        Save configurations in self.configs, and their scores self.scores.
        :param func: Function that takes a configuration and returns a score
        """
        pass
