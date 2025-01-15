import itertools
from typing import Any, Callable


def all_values_combinations(options: dict[str, list[Any]]) -> list[dict[str, Any]]:
    """
    Get all possible combinations of the values in the lists in the dictionary.
    :param options: A dictionary with keys as the configuration keys and values as lists of possible values.
    :return: A list of dictionaries, each dictionary is a possible combination of the values in the lists.
    """
    keys = options.keys()
    values = options.values()
    combinations = list(itertools.product(*values))
    return [dict(zip(keys, combination)) for combination in combinations]


def max_condition_binary_search(min: int, max: int, condition: Callable[[int], bool]) -> int:
    """
    Perform a binary search to find the max value of k such as the condition is True.
    :param min: minimum value of the range
    :param max: maximum value of the range
    :param condition: a function that takes an integer and returns a boolean
    :return: the max value of k such as the condition is True
    """
    while min < max:
        mid = (min + max) // 2
        if condition(mid):
            min = mid + 1
        else:
            max = mid
    return min - 1
