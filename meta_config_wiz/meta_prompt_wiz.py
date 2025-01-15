from typing import Callable, TypeVar, Generic, Type, Literal, Any


from pydantic import BaseModel

from meta_config_wiz.configuration_utils import validate_model_field_types
from meta_config_wiz.strategy.abstract_strategy import AbstractStrategy
from meta_config_wiz.strategy.strategy_factory import strategy_factory
from meta_config_wiz.program_runner.program_runner import ProgramRunner
from meta_config_wiz.program_runner.program_runner_factory import program_runner_factory

ConfigType = TypeVar("ConfigType", bound=BaseModel)
InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class MetaPromptWiz(Generic[ConfigType, InputType, OutputType]):
    """
    * config_class: a subclass of Configuration
    * program: a callable from (Configuration, InputType) to ResultType
    """

    def __init__(self, config_class: Type[ConfigType], program: Callable[[BaseModel, InputType], OutputType]):
        validate_model_field_types(model=config_class)
        self.config_class: ConfigType = config_class
        self.program: Callable[[ConfigType | dict, InputType], OutputType] = program

    def find_best_configuration(self,
                                dataset: list[tuple[InputType, OutputType]],
                                scoring_function: Callable[[OutputType, OutputType], Any] |  Callable[[OutputType], Any],
                                program_runner_name: Literal['AllMean'] = 'AllMean',
                                strategy_name: Literal['RandomStrategy', 'GridStrategy', 'BayesianStrategy'] = 'BayesianStrategy',
                                max_runs: int = 10,
                                strategy_kwargs: dict[str, Any] | None = None) -> ConfigType:
        """
        :param dataset: dataset of [(input, truth_output)]
        :param scoring_function: function that takes pred_output and expected_output, or just pred_output, and returns a score
        :param program_runner_name: which program runner to use. determines how to run the program and aggregate the pred_outputs
        :param strategy_name: which strategy to use. determines how to choose the next configuration to test
        :param max_runs: max total runs to perform
        :param strategy_kwargs:  kwargs to pass to the strategy
        :return:  best configuration
        """

        # init program_runner and strategy
        program_runner: ProgramRunner[InputType, OutputType] = program_runner_factory(program_runner_name=program_runner_name)
        strategy: AbstractStrategy[ConfigType] = strategy_factory(strategy_name=strategy_name, config_class=self.config_class, max_runs=max_runs, strategy_kwargs=strategy_kwargs)
        strategy.run_strategy(func=lambda config: program_runner.run(config=config, program=self.program, dataset=dataset, scoring_function=scoring_function))
        return strategy.choose_best_config()


    def write_all_configurations_results(self,
                                dataset: list[tuple[InputType, OutputType]],
                                scorer: Callable[[OutputType, OutputType], float],
                                program_runner_name: Literal['AllMean'] = 'AllMean',
                                strategy_name: Literal['RandomStrategy', 'GridStrategy', 'BayesianStrategy'] = 'BayesianStrategy',
                                max_runs: int = 10,
                                strategy_kwargs: dict[str, Any] | None = None,
                                results_file: str = 'results.json') -> None:
        """
        writes down all configurations and their results to a file
        """

        # # to just write the configurations, uncomment this block
        # import json
        # strategy: AbstractStrategy[ConfigType] = strategy_factory(strategy_name=strategy_name, config_class=self.config_class, max_runs=max_runs, strategy_kwargs=strategy_kwargs)
        # configs_dicts = [conf.model_dump() for conf in strategy.configs]
        # with open('configs.json', 'w') as f:
        #     json.dump(configs_dicts, f, indent=4)
        # exit()

        # init program_runner and strategy
        strategy: AbstractStrategy[ConfigType] = strategy_factory(strategy_name=strategy_name, config_class=self.config_class, max_runs=max_runs, strategy_kwargs=strategy_kwargs)
        conf_result = []

        # for each config: run and get result, append to conf_result, update the file
        from tqdm import tqdm
        import json
        for conf in tqdm(strategy.configs):
            result = self.program(conf, dataset[0][0])
            conf_result.append({'conf': conf.model_dump(), 'result': result})

            with open(results_file, 'w') as f:
                json.dump(conf_result, f, indent=4)

        with open('configs.json', 'w') as f:
            json.dump(strategy.co, f, indent=4)


