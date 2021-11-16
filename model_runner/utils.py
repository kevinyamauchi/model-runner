import json
import os
from itertools import product
from typing import Any, Dict, List, Tuple, Union

from .validator import ConfigModel


def _create_job_param(
    param_names: List[str],
    param_values: Tuple[Any],
    job_prefix: str,
    runner: str,
    output_base_dir: str,
    job_index: int,
) -> Dict[str, Any]:

    params = {k: v for k, v in zip(param_names, param_values)}
    params.update(
        {
            "job_prefix": job_prefix,
            "runner": runner,
            "output_base_dir": output_base_dir,
            "job_index": job_index,
        }
    )
    return params


def _create_job_array_params(
    job_params: Dict[str, List[Any]],
    job_prefix: str,
    runner: str,
    output_base_dir: str,
) -> Dict[int, Dict[str, Any]]:

    param_names = list(job_params.keys())
    param_values = list(job_params.values())

    param_combinations = product(*param_values)

    job_array_params = {
        i: _create_job_param(
            param_names=param_names,
            param_values=values,
            job_prefix=job_prefix,
            runner=runner,
            output_base_dir=output_base_dir,
            job_index=i,
        )
        for i, values in enumerate(param_combinations, start=1)
    }

    return job_array_params


def write_runner_params(
    array_config: ConfigModel, output_path: Union[str, os.PathLike]
):
    """Write the parameters file for the job array runners to disk

    Parameters
    ----------
    array_config : ConfigModel
        The parameters for the job array. The dictionary should have
        string keys, each being a parameter name. The values should be
        a list of values. The resulting job array will have jobs that are
        the combinations of all of the parameters.

    output_path : os.PathLike
        The path to the file to save the job array parameters to.
        Should have the extension .json.
    """
    job_params = array_config.runner_parameters
    job_array_params = _create_job_array_params(
        job_params,
        job_prefix=array_config.job_prefix,
        runner=array_config.runner,
        output_base_dir=array_config.output_base_dir,
    )

    with open(output_path, "w") as f_out:
        json.dump(job_array_params, f_out)
