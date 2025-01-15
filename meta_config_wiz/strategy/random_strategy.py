from typing import Any, Type, Generic, Callable

from sklearn.model_selection import ParameterSampler

from meta_config_wiz.strategy.abstract_strategy import AbstractStrategy, ConfigType
from meta_config_wiz.configuration_utils import model_key2k_possible_values


class RandomStrategy(AbstractStrategy[ConfigType], Generic[ConfigType]):
    """test random configurations for max_runs times"""

    def __init__(self, config_class_type: Type[ConfigType], max_runs: int = 100):
        super().__init__(config_class_type=config_class_type, max_runs=max_runs)

        key2k_possible_values: dict[str, list[Any]] = model_key2k_possible_values(model=self.config_class_type, k=max_runs)
        config_dicts: list[dict[str, Any]] = list(ParameterSampler(param_distributions=key2k_possible_values, n_iter=max_runs, random_state=42))

        # make a list of configuration classes out of all possible values combinations
        # invalid configurations will be skipped, and we wil not make another instead of them
        self.configs: list[ConfigType] = []
        for config_dict in config_dicts:
            try:
                # create a new configuration instance from config_dict. if we don't have it yet (we could have it already, example in the readme), add it to the list
                new_config: ConfigType = self.config_class_type(**config_dict)
                self.configs.append(new_config)
            # we will get an error if the config_dict is not a valid configuration
            except ValueError:
                pass

    def run_strategy(self, func: Callable[[ConfigType], float], **kwargs) -> None:
        """
        :param func: function that takes a configuration and returns a score
        """
        for config in self.configs:
            score: float = func(config)
            self.scores.append(score)


