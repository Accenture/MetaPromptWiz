from pydantic import BaseModel
from abc import ABC


class EvaluationScore(BaseModel, ABC):
    """
    Abstract class to hold evaluation scores for a configuration (e.g., accuracy, f1, cost, running_time, etc.)    
    """
    pass

class ConfigurationScore(BaseModel):
    """
    A representation of the score of a configuration supported by an exploration strategy
    E.g., float, vector, etc.
    """
    pass
    
    def __add__(self, other: 'ConfigurationScore') -> 'ConfigurationScore':
        pass

    def __radd__(self, other: 'ConfigurationScore') -> 'ConfigurationScore':
        pass

    def __sub__(self, other: 'ConfigurationScore') -> 'ConfigurationScore':
        pass

    def __rsub__(self, other: 'ConfigurationScore') -> 'ConfigurationScore':
        pass

    def __lt__(self, other: 'ConfigurationScore') -> bool:
        pass

    def __gt__(self, other: 'ConfigurationScore') -> bool:
        pass

    def __eq__(self, other: 'ConfigurationScore') -> bool:
        pass

    def __sum__(self, other: 'ConfigurationScore') -> 'ConfigurationScore':
        pass