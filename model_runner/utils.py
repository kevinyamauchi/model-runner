import json
import os
from itertools import product
from typing import Any, Dict, List, Tuple, Union


def _create_job_param(
    param_names: List[str], param_values: Tuple[Any]
) -> Dict[str, Any]:
    return {k: v for k, v in zip(param_names, param_values)}


def _create_job_array_params(params: Dict[str, List[Any]]) -> Dict[int, Dict[str, Any]]:

    param_names = list(params.keys())
    param_values = list(params.values())

    param_combinations = product(*param_values)

    job_array_params = {
        i: _create_job_param(param_names, values)
        for i, values in enumerate(param_combinations, start=1)
    }

    return job_array_params


def write_runner_params(
    params: Dict[str, List[Any]], output_path: Union[str, os.PathLike]
):
    """Write the parameters file for the job array runners to disk

    Parameters
    ----------
    params : Dict[str, List[Any]]
        The parameters for the job array. The dictionary should have
        string keys, each being a parameter name. The values should be
        a list of values. The resulting job array will have jobs that are
        the combinations of all of the parameters.

    output_path : os.PathLike
        The path to the file to save the job array parameters to.
        Should have the extension .json.
    """

    job_array_params = _create_job_array_params(params)

    with open(output_path, "w") as f_out:
        json.dump(job_array_params, f_out)
