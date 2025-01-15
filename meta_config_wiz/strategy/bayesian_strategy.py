from typing import Any, Type, Generic, Callable, get_args
from bayes_opt import BayesianOptimization

from meta_config_wiz.strategy.abstract_strategy import AbstractStrategy, ConfigType
from meta_config_wiz.configuration_utils import get_numeric_param_min, get_numeric_param_max


class BayesianStrategy(AbstractStrategy[ConfigType], Generic[ConfigType]):
    """
    use Bayesian optimization to maximize the score of the program
    The Bayesian optimization works where all parameters have a float range,
    To overcome this we convert all parameters to float before feeding them to the optimizer, and convert them back to their original values after getting the result
    Based on this tutorial: https://bayesian-optimization.github.io/BayesianOptimization/advanced-tour.html#2.-Dealing-with-discrete-parameters
    """

    def __init__(
        self,
        config_class_type: Type[ConfigType],
        max_runs: int = -1,
        min_score: float = -1,
    ):
        """
        Define the Bayesian optimization optimizer and a default value for invalid configurations
        """
        super().__init__(config_class_type=config_class_type, max_runs=max_runs)
        self.min_score: float = min_score  # will be considered as output of the optimized function if the configuration is invalid

    def config_numeric2value(self, key: str, numeric_value: float) -> Any:
        """
        Convert a numeric value of a parameter to its original value.
        This method takes a numeric representation of a parameter and converts it back to its original value based on the parameter's type.

        Args:
            key (str): The name of the parameter.
            numeric_value (float): The numeric value of the parameter.

        Returns:
            Any: The original value from the configuration. The return type depends on the parameter's type:
                - If the parameter is a float, the same float value is returned.
                - If the parameter is an int, the value is rounded and returned as an int.
                - If the parameter is a bool, the value is converted to a boolean.
                - If the parameter is a Literal, the corresponding value from the possible values is returned.
        """
        field_info = self.config_class_type.model_fields[key]
        if field_info.annotation.__name__ == "float":
            return numeric_value
        elif field_info.annotation.__name__ == "int":
            return int(numeric_value)
        elif field_info.annotation.__name__ == "bool":
            return bool(int(numeric_value))
        elif field_info.annotation.__name__ == "Literal":
            possible_values: list[Any] = self.config_class_type.model_fields[
                key
            ].annotation.__args__
            if int(numeric_value) >= len(possible_values):
                return possible_values[-1]
            elif int(numeric_value) < 0:
                return possible_values[0]
            else:
                return possible_values[int(numeric_value)]

    def param2numeric_range(self) -> dict[str, tuple[float, float]]:
        """
        Generates a dictionary mapping parameter names to their numeric ranges.

        This method iterates over the fields of the configuration class type and
        determines the numeric range for each parameter based on its type annotation.
        For parameters annotated as float or int, it retrieves the minimum and maximum
        values using `get_numeric_param_min` and `get_numeric_param_max` functions.
        For boolean parameters, it assigns a range of (0, 1).
        For other types, it assigns a range based on the length of the possible values.

        :return: A dictionary where the keys are parameter names and the values are
                 tuples representing the numeric range (min, max) for each parameter.
        """
        param2numeric_range: dict[str, tuple[float, float]] = dict()
        for field_name, field_info in self.config_class_type.model_fields.items():
            if field_info.annotation.__name__ in ["float", "int"]:
                param2numeric_range[field_name] = (
                    get_numeric_param_min(self.config_class_type, field_name),
                    get_numeric_param_max(self.config_class_type, field_name),
                )
            elif field_info.annotation.__name__ == "bool":
                param2numeric_range[field_name] = (0, 1)
            else:
                param2numeric_range[field_name] = (
                    0,
                    len(get_args(field_info.annotation)) - 1,
                )
        return param2numeric_range

    def run_strategy(self, func: Callable[[ConfigType], float], **kwargs) -> None:
        """
        maximize the score of the function func
        save configuration tested and their scores in configs and scores fields
        :param func: function that takes a configuration and returns a score
        """

        # function to pass the optimizer
        def numeric_params2func_call(**kwargs) -> float:
            """
            Converts numeric parameter values to their original values, constructs the configuration object, and calls the function.
            
            :param kwargs: A dictionary of {<param_name>: <numeric_value>} for each parameter in the configuration.
            :return: The output of the function after converting the numeric values to their original values and constructing the configuration object.
            
            If the configuration is not valid, returns the minimum score. The final output, which is the configuration with the maximum score, will be valid.
            """
            try:
                config: ConfigType = self.config_class_type(
                    **{
                        key: self.config_numeric2value(key, numeric_value)
                        for key, numeric_value in kwargs.items()
                    }
                )
                return func(config)
            except ValueError:
                return self.min_score

        # define optimizer
        optimizer = BayesianOptimization(
            f=numeric_params2func_call,
            pbounds=self.param2numeric_range(),
            verbose=0,  # verbose = 2 prints score of every configuration tested, verbose = 1 prints only when a maximum is observed, verbose = 0 is silent
            random_state=1,
        )

        # run optimizer
        optimizer.maximize(
            init_points=self.max_runs // 4,
            n_iter=self.max_runs // 4 * 3,
        )

        # convert results parameter dictionaries to configuration classes, save configurations and scores
        for result_dict in optimizer.res:
            params, score = result_dict["params"], result_dict["target"]
            try:
                config = self.config_class_type(
                    **{
                        key: self.config_numeric2value(key, numeric_value)
                        for key, numeric_value in params.items()
                    }
                )
                self.configs.append(config)
                self.scores.append(score)
            except ValueError:  # skip invalid configurations
                pass
