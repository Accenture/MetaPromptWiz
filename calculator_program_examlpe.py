from pydantic import BaseModel, Field, model_validator
from typing import Literal
import numpy as np

from meta_config_wiz import MetaPromptWiz

import logging
logging.basicConfig(level=logging.INFO)

# Define the input and output types
input_type = tuple[float, float]
output_type = float


# Define the program configuration class
class MyConfiguration(BaseModel):
    calculation_mode: Literal["linear", "quadratic"] = "linear"
    linear_factor: float = Field(default=1.0, ge=0.0, le=10)  # Multiplier for linear calculations
    quadratic_factor: float = Field(default=0.5, ge=0.0, le=10)  # Multiplier for quadratic terms
    offset: float = Field(default=6, gt=0, lt=10)  # Constant term added to the result

    # note that using that validator will make most of the configurations invalid. We skip them, so we will have to use a high value of max_runs
    @model_validator(mode='after')
    @classmethod
    def set_unused_factor_to_zero(cls, config):
        """if linear or quadratic calculation mode is not used, make sure the unused factor to zero"""
        if config.calculation_mode == 'quadratic':
            if config.linear_factor != 0:
                raise ValueError("Linear factor must be 0 when using quadratic calculation mode")
        if config.calculation_mode == 'linear':
            if config.quadratic_factor != 0:
                raise ValueError("Quadratic factor must be 0 when using linear calculation mode")

# Define the program and scorer
def my_program(config: MyConfiguration, input: input_type) -> output_type:
    # Unpack the input
    x, y = input
    # Calculate the result
    if config.calculation_mode == "linear":
        result = config.linear_factor * (x + y) + config.offset
    elif config.calculation_mode == "quadratic":
        result = config.quadratic_factor * (x ** 2 + y ** 2) + config.offset
    else:
        raise ValueError("Invalid calculation mode")
    # Return the result
    return result


# Define a custom scorer
def my_scorer(result_pred: output_type, result_true: output_type) -> float:
    distance = abs(result_pred - result_true)
    return 1 / (1 + distance)   # 1 + distance is always greater than 1, so the score will be between 0 and 1


# Generate a biased dataset
def generate_biased_dataset(size: int, config: MyConfiguration, add_noise: bool = True) -> list[tuple[input_type, output_type]]:
    dataset = []
    for _ in range(size):
        input_data = (np.random.rand(), np.random.rand())
        true_result = my_program(config, input_data)
        if add_noise:
            true_result += np.random.normal(0, 0.1)
        dataset.append((input_data, true_result))
    return dataset


configuration_truth: MyConfiguration = MyConfiguration(calculation_mode='linear', linear_factor=4.0, quadratic_factor=0, offset=8)
my_dataset: list[tuple[input_type, output_type]] = generate_biased_dataset(size=100, config=configuration_truth)


# Create a ConfigWiz instance and find the best configuration
my_config_wiz = MetaPromptWiz[MyConfiguration, input_type, output_type](config_class=MyConfiguration, program=my_program)
best_configuration: MyConfiguration = my_config_wiz.find_best_configuration(dataset=my_dataset, scoring_function=my_scorer, program_runner_name='AllMean', strategy_name='GridStrategy', max_runs=4000)
for field, value in best_configuration.model_dump().items():
    print(f"{field}: {value}")
