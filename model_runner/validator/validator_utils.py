# input: path to settings file (e.g. .json file)
#   1. path to data --> test: string, path exists OK
#   2. program to run --> test: string, file exists OK
#   3. settings for job array
#     * #gpus --> test: int OK
#     * gpu type --> test: str, in list of existing GPUs OK
#     * #processor cores: --> test: int OK
#     * memory per processor core --> test: int OK
#     * scratch per processor core --> test: int OK
#     * run_time --> test: str or int, either in min or [h] format OK
#     * #jobs to run --> test: int OK
#     * #jobs to run in parallel --> test: int OK
#     * log-file name template --> test: str OK
#   4. hyper-parameter margins (+dtype) --> test: Dict[str, List[Any]], OK
# output: None

# NOTE: for now the hyper-parameter grid has to be submitted explicitly
# TODO: later patch explicit version to also accomodate continuous ranges, discrete variables, ...
# TODO: include feature to check if required resources can be allocated to a single machine or require multiple machines
# TODO: set up tests for input function in _tests
# TODO: include type coercion

import os
from typing import Any, Dict, List, Union

from pydantic import BaseModel, validator


class JobArrayModel(BaseModel):
    run_time: Union[str, int]
    processor_cores: int
    memory: int
    scratch: int
    gpu_type: str
    ngpus: int
    njobs: int
    njobs_parallel: int
    logfile_name_template: str

    @validator("gpu_type")
    def validate_gpu_type(cls, v):
        """
        Validates if submitted gpu_type is currently available at Euler
        (https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#GPU).
        """
        gpu_list = [
            "GeForceGTX1080",
            "GeForceGTX1080Ti",
            "GeForceRTX2080Ti",
            "GeForceRTX2080Ti",
            "TITANRTX",
            "TeslaV100_SXM2_32GB",
            "TeslaV100_SXM2_32GB",
            "A100_PCIE_40GB",
        ]

        if v not in gpu_list:
            raise ValueError(
                f'"{v}" is currently not available on Euler. Check the list of available GPUs '
                "at https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#GPU."
            )

        return v

    @validator("run_time")
    def validate_and_coerce_run_time(cls, v):
        """
        Validates if submitted run_time adheres to the format specified in
        https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#Wall-clock_time.
        """
        if type(v) == str:
            v_split = v.split(":")
            if len(v_split) == 1:
                try:
                    minutes = int(v_split[0])
                    v = minutes
                except ValueError:
                    raise ValueError(
                        "run_time string must adhere to the format specified in "
                        "https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#Wall-clock_time."
                    )
            elif len(v_split) == 2:
                try:
                    minutes = int(v_split[1])
                    if (minutes > 59) or (minutes < 0):
                        raise ValueError(
                            "run_time string must adhere to the format specified in "
                            "https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#Wall-clock_time."
                        )

                    hours = int(v_split[0])
                    v = minutes + hours * 60
                except ValueError:
                    raise ValueError(
                        "run_time string must adhere to the format specified in "
                        "https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#Wall-clock_time."
                    )
            else:
                raise ValueError(
                    "run_time string must adhere to the format specified in "
                    "https://scicomp.ethz.ch/wiki/Getting_started_with_clusters#Wall-clock_time."
                )

        return v


class ConfigModel(BaseModel):
    data: str
    runner: str
    job_array: JobArrayModel
    hyperparameters: Dict[str, List[Any]]

    @validator("data")
    def data_is_file_or_path(cls, v):
        if not (os.path.isfile(v) or os.path.isdir(v)):
            raise ValueError('"data" is not a file/directory.')
        else:
            if os.path.isdir(v) and v[-1] != "/":
                return v + "/"
        return v

    @validator("runner")
    def runner_is_file(cls, v):
        if not os.path.isfile(v):
            raise ValueError('"runner" is not a file.')
        return v
