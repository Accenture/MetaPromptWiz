from typing import Any, Type, get_args
import numpy as np
from annotated_types import Gt, Ge, Lt, Le
from pydantic import BaseModel
import random


def validate_model_field_types(model: BaseModel | Type[BaseModel], allowed_types: list[str] = None) -> None:
    """
    Validates the types of all fields in a Pydantic model.
    :param model: The Pydantic model class.
    :param allowed_types: A list of allowed types for the fields. Default is ['int', 'float', 'bool', 'Literal'].
    :raises AssertionError: If a field has an invalid type
    """
    allowed_types = allowed_types or ['int', 'float', 'bool', 'Literal']
    for field_name, field_info in model.model_fields.items():
        field_type_name = field_info.annotation.__name__
        assert field_type_name in allowed_types, f"Field {field_name} has an invalid type {field_type_name}."


def get_numeric_param_max(model: BaseModel | Type[BaseModel], param: str) -> int | float:
    """
    Gets the maximum value of a parameter in a Pydantic model.
    for int parameter we return  le or lt-1
    for float parameter we return le or lt-1e-10
    :param model: The Pydantic model class.
    :param param: The parameter name.
    :return: The maximum value of the parameter.
    :raises AssertionError: If the parameter is not found in the model.
    :raises ValueError: If the parameter is not numeric
    """
    assert param in model.model_fields, f"Parameter {param} not found in model {model}. existing parameters: {list(model.model_fields.keys())}"
    field_info = model.model_fields[param]
    if field_info.annotation.__name__ == 'int':
        if any(isinstance(restriction, Lt) for restriction in field_info.metadata):
            return int([restriction for restriction in field_info.metadata if isinstance(restriction, Lt)][0].lt - 1)
        else:
            return int([restriction for restriction in field_info.metadata if isinstance(restriction, Le)][0].le)
    elif field_info.annotation.__name__ == 'float':
        if any(isinstance(restriction, Lt) for restriction in field_info.metadata):
            return float([restriction for restriction in field_info.metadata if isinstance(restriction, Lt)][0].lt - 1e-10)
        else:
            return float([restriction for restriction in field_info.metadata if isinstance(restriction, Le)][0].le)
    else:
        raise ValueError(f"Parameter {param} is not int or float.")


def get_numeric_param_min(model: BaseModel | Type[BaseModel], param: str) -> int | float:
    """
    Gets the minimum value of a parameter in a Pydantic model.
    for int parameter we return  ge or gt+1
    for float parameter we return ge or gt+1e-10
    :param model: The Pydantic model class.
    :param param: The parameter name.
    :return: The minimum value of the parameter.
    :raises AssertionError: If the parameter is not found in the model.
    :raises ValueError: If the parameter is not numeric
    """
    assert param in model.model_fields, f"Parameter {param} not found in model {model}. existing parameters: {list(model.model_fields.keys())}"
    field_info = model.model_fields[param]
    if field_info.annotation.__name__ == 'int':
        if any(isinstance(restriction, Gt) for restriction in field_info.metadata):
            return int([restriction for restriction in field_info.metadata if isinstance(restriction, Gt)][0].gt + 1)
        else:
            return int([restriction for restriction in field_info.metadata if isinstance(restriction, Ge)][0].ge)
    elif field_info.annotation.__name__ == 'float':
        if any(isinstance(restriction, Gt) for restriction in field_info.metadata):
            return float([restriction for restriction in field_info.metadata if isinstance(restriction, Gt)][0].gt + 1e-10)
        else:
            return float([restriction for restriction in field_info.metadata if isinstance(restriction, Ge)][0].ge)
    else:
        raise ValueError(f"Parameter {param} is not int or float.")


def model_key2k_possible_values(model: BaseModel | Type[BaseModel], k: int) -> dict[str, list[Any]]:
    """
    Generates `k` example values for each key in the configuration.
    :param model: pydantic model
    :param k: The number of example values to generate for each key.
    :return: A dictionary with keys as the configuration keys and values as lists of `k` example values.
    :raises AssertionError: If `k` is less than or equal to 0.
    """
    assert k > 0, "k must be greater than 0"
    # init empty dictionary to store possible values for each key
    key2possible_values: dict[str, list[Any]] = {}

    # for each field in the model, get the possible values
    for field_name, field_info in model.model_fields.items():
        try:
            match field_info.annotation.__name__:
                # int field -> extract min and max from metadata, return k evenly spaced values between min and max
                case 'int':
                    min_value, max_value = get_numeric_param_min(model, field_name), get_numeric_param_max(model, field_name)
                    key2possible_values[field_name] = list(set(np.linspace(start=min_value, stop=max_value, num=k, dtype=int)))  # there will be duplicates if k is greater than the range
                # float field -> do the same as for int field
                case 'float':
                    min_value, max_value = get_numeric_param_min(model, field_name), get_numeric_param_max(model, field_name)
                    key2possible_values[field_name] = np.linspace(start=min_value, stop=max_value, num=k, dtype=float).tolist()
                # bool field -> possible values are True and False
                case 'bool':
                    possible_values = [False, True]
                    key2possible_values[field_name] = random.sample(possible_values, min(k, len(possible_values)))
                # literal field -> extract possible values from annotation
                case 'Literal':
                    possible_values = list(get_args(field_info.annotation))
                    key2possible_values[field_name] = random.sample(possible_values, min(k, len(possible_values)))
                case _:
                    raise ValueError(f"Field '{field_name}' has an invalid type {field_info.annotation.__name__}.")
        except IndexError as e:
            print(f"Error while generating possible values for field '{field_name}': {e}\nmake sure that the field type is one of ['int', 'float', 'bool', 'Literal'] and you are not using thinks like confloat or conint")

    # return dictionary with possible values for each key
    return key2possible_values
