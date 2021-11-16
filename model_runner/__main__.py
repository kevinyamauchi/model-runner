import argparse
import os

from .utils import write_job_array, write_runner_params
from .validator import _validation_func


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", help="path to the job params file", type=str)
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
        params=validated_parameters.runner_params.dict(), output_path=runner_params_path
    )

    # build the submission command from parameters
    job_prefix = validated_parameters["job_prefix"]
    njobs_parallel = validated_parameters["job_parameters"]["njobs_parallel"]
    job_array_command = write_job_array(runner_params_path, job_prefix, njobs_parallel)

    # submit the job
    os.system(job_array_command)
