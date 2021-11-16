import argparse
import json
import os
from typing import Union

from .utils import write_runner_params
from .validator import ConfigModel


def _validation_func(params_path: Union[str, os.PathLike]) -> ConfigModel:
    with open(params_path, "r") as f:
        parameters = json.load(f)
    validated_parameters = ConfigModel(**parameters)
    return validated_parameters


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="path to the job params file", type=str)
    args = parser.parse_args()

    return args


def main():
    args = _parse_args()
    validated_parameters = _validation_func(args.params)

    # create and write the runner params
    runner_params_fname = f"{validated_parameters.job_prefix}_runner_parameters.json"
    runner_params_path = os.path.join(
        validated_parameters.output_base_dir, runner_params_fname
    )
    write_runner_params(
        array_config=validated_parameters.dict(), output_path=runner_params_path
    )

    # build the submission command from parameters

    # submit the job
