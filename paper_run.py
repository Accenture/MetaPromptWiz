from random import random
from meta_config_wiz.applications.text2sql import Text2SQLConfiguration
from meta_config_wiz import MetaPromptWiz
from meta_config_wiz.program_runner.program_runner import InputType, OutputType
from meta_config_wiz.applications.text2sql import Text2SQLSampleScore, Text2SQLConfigurationScore
from meta_config_wiz.strategy.evalautor import ConfigurationEvaluator, SampleEvaluator

TextToSQLOutput = Text2SQLSampleScore


class TextToSQLConfigurationEvaluator(ConfigurationEvaluator):
    """
    Evaluator for the Text to SQL task
    Aggregate the scores by taking only the total execution match score
    """

    def __call__(
        self, predicted_output: str, expected_output: str
    ) -> Text2SQLConfigurationScore:
        # stub implementation
        score = TextToSQLEvaluator()(predicted_output, expected_output)
        numberic_score = 1 if score.execution_match else 0
        return Text2SQLConfigurationScore(execution_match=numberic_score)


class TextToSQLEvaluator(SampleEvaluator):
    """
    Evaluator for the Text to SQL task
    Runs the configuration on a benchmark, and returns the scores
    """

    def __call__(
        self, output_pred: OutputType, expected_output: OutputType
    ) -> Text2SQLSampleScore:
        # stub implementation
        is_exact_match = random() > 0.5
        cost = random() * 100
        time = random()
        # number_of_errors random integer between 0 and 5
        number_of_errors = int(random() * 5)

        return Text2SQLSampleScore(
            execution_match=is_exact_match,
            execution_time=time,
            number_of_errors=number_of_errors,
            cost=cost,
        )


def run_text2sql(conf: Text2SQLConfiguration, dummy_input: InputType) -> OutputType:
    """ "
    Runs configuration on an evaluation benchmark, and returns evaluation measures
    """
    #  generate random string
    return "SELECT * FROM table WHERE column = '{value}'".format(value=random())


# Example usage, using a mock program that generates random SQL queries and a mock evaluator that generates random scores
my_config_wiz = MetaPromptWiz[Text2SQLConfiguration, str, str](
    config_class=Text2SQLConfiguration, program=run_text2sql
)
dataset = []
for i in range(100):
    dataset.append((f"question_{i}", f"query_{i}"))
best_config: Text2SQLConfiguration = my_config_wiz.find_best_configuration(
    dataset=dataset,
    scoring_function=TextToSQLConfigurationEvaluator(),
    program_runner_name="AllMean",
    strategy_name="RandomStrategy",
    max_runs=5,
)

print(best_config)
