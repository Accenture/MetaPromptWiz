from pydantic import model_validator
from typing import Literal, Dict
from meta_config_wiz.models.configurations import Configuration
from meta_config_wiz.models.scores import ConfigurationScore, EvaluationScore
from pydantic import BaseModel




class Text2SQLConfiguration(Configuration):
    """
    Configuration for the Text2SQL task.
    prompt_style - one of: InstructiveStyle, DailSqlStyle, ConciseStyle
    example_selector - one of: RandomExampleSelector, MaxMarginalRelevanceExampleSelector, SemanticSimilarityExampleSelector
    examples_number - one of: 1, 10, 20, 40
    error_correction - bool
    llm - one of: gpt_35, gpt_4
    """

    prompt_style: Literal["InstructiveStyle", "DailSqlStyle", "ConciseStyle"]
    example_selector: Literal[
        "RandomExampleSelector",
        "MaxMarginalRelevanceExampleSelector",
        "SemanticSimilarityExampleSelector",
    ]
    examples_number: Literal[1, 10, 20, 40]
    error_correction: bool
    llm: Literal["gpt_35", "gpt_4"]

    @model_validator(mode="after")
    def concise_prompt_validator(self) -> "Text2SQLConfiguration":
        """
        Validates an SQL configuration.
        Concise prompt style must have examples_number=1 and example_selector=RandomExampleSelector.
        Raise error for configurations that do not meet this requirement.
        """
        if self.prompt_style == "ConciseStyle":
            if (
                self.examples_number != 1
                or self.example_selector != "RandomExampleSelector"
            ):
                raise ValueError("ConciseStyle prompt does not use examples")
        return self


class Text2SQLSampleScore(EvaluationScore):
    """
    Scores for the Text to SQL task
    Execution_match - dictionary of hardness level to execution match score. 'total' is the weighted mean
    Execution_time - execution time in seconds
    Errors_number - number of errors we encountered during execution
    """

    execution_match: bool
    execution_time: float
    number_of_errors: int
    cost: float


class Text2SQLConfigurationScore(ConfigurationScore):
    """
    Aggregated score for the Text to SQL task
    """

    execution_match: float

    def __add__(self, other):
        if isinstance(other, Text2SQLConfigurationScore):
            return Text2SQLConfigurationScore(execution_match=self.execution_match + other.execution_match)
        elif isinstance(other, (int, float)):
            return Text2SQLConfigurationScore(execution_match=self.execution_match + other)
        else:
            return NotImplemented
        
    # left addition and right addition
    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, Text2SQLConfigurationScore):
            return Text2SQLConfigurationScore(execution_match=self.execution_match - other.execution_match)
        elif isinstance(other, (int, float)):
            return Text2SQLConfigurationScore(execution_match=self.execution_match - other)
        else:
            return NotImplemented
        
    # left subtraction
    def __rsub__(self, other):
        if isinstance(other, Text2SQLConfigurationScore):
            return Text2SQLConfigurationScore(execution_match=other.execution_match - self.execution_match)
        elif isinstance(other, (int, float)):
            return Text2SQLConfigurationScore(execution_match=other - self.execution_match)
        else:
            return NotImplemented
        
    def __lt__(self, other):
        assert isinstance(other, Text2SQLConfigurationScore)
        return self.execution_match < other.execution_match
    
    def __gt__(self, other):
        assert isinstance(other, Text2SQLConfigurationScore)
        return self.execution_match > other.execution_match
    
    def __eq__(self, other):
        assert isinstance(other, Text2SQLConfigurationScore)
        return self.execution_match == other.execution_match
    
    def __sum__(self, other):
        if isinstance(other, Text2SQLConfigurationScore):
            return Text2SQLConfigurationScore(execution_match=self.execution_match + other.execution_match)
        elif isinstance(other, (int, float)):
            return Text2SQLConfigurationScore(execution_match=self.execution_match + other)
        else:
            return NotImplemented
        
    def __truediv__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            return self.execution_match / other