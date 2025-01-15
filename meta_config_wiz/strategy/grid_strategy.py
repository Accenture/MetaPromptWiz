from typing import Any, Type, Generic, Callable
from sklearn.model_selection import ParameterGrid
from random import shuffle

from meta_config_wiz.strategy.abstract_strategy import AbstractStrategy, ConfigType
from meta_config_wiz.configuration_utils import model_key2k_possible_values


class GridStrategy(AbstractStrategy[ConfigType], Generic[ConfigType]):
    """
    runs tests of on equally distributed possible values for each field in a grid search fashion
    """

    def __init__(self, config_class_type: Type[ConfigType], max_runs: int = 100):
        super().__init__(config_class_type=config_class_type, max_runs=max_runs)

        # try until k = max_runs, at that point we probably don't have any more configurations to try
        for k in range(1, max_runs + 1):
            # get a list of all possible configurations for this k
            key2k_possible_values: dict[str, list[Any]] = model_key2k_possible_values(model=self.config_class_type, k=k)
            cur_config_dicts: list[dict[str, Any]] = list(ParameterGrid(param_grid=key2k_possible_values))
            # shuffle because if the number of possible configurations is greater that max_runs, we want a random sample
            shuffle(cur_config_dicts)
            # try adding all configurations to the list, if we reach max_runs, break
            while len(self.configs) < max_runs and len(cur_config_dicts) > 0:
                try:
                    new_config: ConfigType = self.config_class_type(**cur_config_dicts.pop())
                    self.configs.append(new_config)
                except ValueError:  # invalid configuration - raises ValueError by Pydantic validator
                    pass

            # if we got all configuration we need, break
            if len(self.configs) >= max_runs:
                break
            # if we still need more configurations, clear config_dicts because we will build it from scratch next iteration
            if len(cur_config_dicts) == 0:
                self.configs.clear()


    def run_strategy(self, func: Callable[[ConfigType], float], **kwargs) -> None:
        """
        :param func: function that takes a configuration and returns a score
        """
        for config in self.configs:
            score: float = func(config)
            self.scores.append(score)

