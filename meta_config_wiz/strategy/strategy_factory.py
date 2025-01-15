from typing import Literal, Type

from pydantic import BaseModel

from meta_config_wiz.strategy.abstract_strategy import AbstractStrategy
from meta_config_wiz.strategy.random_strategy import RandomStrategy
from meta_config_wiz.strategy.grid_strategy import GridStrategy
from meta_config_wiz.strategy.bayesian_strategy import BayesianStrategy


def strategy_factory(strategy_name: Literal['RandomStrategy', 'GridStrategy', 'BayesianStrategy'], config_class: Type[BaseModel], max_runs: int = -1, strategy_kwargs: dict[str, any] | None = None) -> AbstractStrategy:
    """
    Factory method for creating strategy instances
    :param strategy_name: name of the strategy to create
    :param config_class: class of the configuration
    :param max_runs: maximum number of runs for the strategy. some strategies may want to know it beforehand.
    :return: instance of the strategy
    """
    match strategy_name:
        case 'RandomStrategy':
            return RandomStrategy[config_class](config_class_type=config_class, max_runs=max_runs, **(strategy_kwargs or {}))
        case 'GridStrategy':
            return GridStrategy[config_class](config_class_type=config_class, max_runs=max_runs, **(strategy_kwargs or {}))
        case 'BayesianStrategy':
            return BayesianStrategy[config_class](config_class_type=config_class, max_runs=max_runs, **(strategy_kwargs or {}))
        case _:
            raise ValueError(f"Unknown strategy name: {strategy_name}")