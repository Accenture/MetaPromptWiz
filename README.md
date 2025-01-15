# MetaPromptWiz
MetaPromptWiz is a package that aims to explore configurations for LLM Applications. 
It takes a program and uses a different search strategies to find promising configuration.

## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install MetaPromptWiz, you can use `pip`:
```sh
pip install config-wiz
```

Or add it to your `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
config-wiz = "^0.0.5"
```

## Usage
To get the best configuration for your program, follow these steps:

1. Construct a `MetaPromptWiz` object with the following arguments:
   - **Configuration Class**: A Pydantic model. All fields must be one of: `Literal`, `bool`, `int/float` with both `ge/gt` and `le/lt` constraints. You can use Pydantic's field and model validators, but note that invalid configurations will be skipped, although they will count as a run, so you should set a high value for `max_runs`.
   - **Program**: A function of `(configuration, program_input_type) -> program_output_type`.
   - **SampleScore**: A set of scores for a single input of over the evaluted configuration
   - **ConfigurationScore**: A scoring function that projects the sample score to the metric of the exploration stratgey (e.g., float)

2. Call the `find_best_configuration` method with the following arguments:
   - **Dataset**: A dataset of `[(input, truth_output)]`.
   - **Scoring function**: A function of `(program_output, expected_output[optional]) -> score`. Higher scores mean the program output is closer to the truth output.
   - **Program_Runner_Name**: A string. Choose one from our program runners. Determines how to get the score of a specific configuration, program, and dataset. For example, run the program on all samples in the dataset, score all outputs, and return the mean score.
   - **Strategy_Name**: A string. Choose one from our strategies. Determines which configurations to try next based on previous configurations and their scores. For example, grid search.
   - **Max_runs**: An integer. The maximum number of times to run the program with different configurations.

## Examples
Consider the running examlpe provided in paper_run.py, which shows exploration of a Text2SQL application.


## Contributing
We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more information.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.