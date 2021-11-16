import json
import os
from typing import Any, Dict, List, Union

from pydantic import BaseModel, validator


class JobArrayModel(BaseModel):
    """
    pydantic BaseModel that handles the job_parameters.

    Parameters
    ----------
    run_time: Union[str, int]
        The time resources on the compute note are reservered for a single job. Corresponds to the bsub "-W"-flag.
    processor_cores: int
        Number of processor cores requested for a single job. Corresponds to the bsub "-n"-flag.
    memory: int
        Amount of memory requested per processor core. Corresponds to bsub -R "rusage[mem={memory}]".
    scratch: int
        Amount of local scratch requested per processor core. Corresponds to bsub -R "rusage[scratch={scratch}]".
    gpu_type: str
        Type of gpu that is accepted by bsub -R "select[gpu_model0=={gpu_type}]".
    ngpus: int
        Number of GPUs of {gpu_type} requested. Corresponds to bsub -R "rusage[ngpus_excl_p={ngpus}]".
    njobs_parallel: int
        Number of jobs the job array will submit in parallel.
    logfile_dir: str
        Path to directory to which lsf output files are saved.
    """

    run_time: Union[str, int]
    processor_cores: int
    memory: int
    scratch: int
    gpu_type: str
    ngpus: int
    njobs_parallel: int
    logfile_dir: str

    @validator("logfile_dir")
    def logfile_dir_is_dir(cls, v):
        """
        Validate if logfile_dir is an existing directory.
        """
        if not os.path.isdir(v):
            raise ValueError(f'"{v}" is not a directory.')
        elif not v.endswith(os.path.sep):
            v += os.path.sep

        return v

    @validator("gpu_type")
    def gpu_type_exists(cls, v):
        """
        Validate if submitted gpu_type is currently available at Euler
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
        Validate if submitted run_time adheres to the format specified in
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
    """
    pydantic BaseModel that handles the job_config.json.

    Parameters
    ----------
    runner: str
        Path to the runner file.
    job_prefix: str
        Prefix that precedes all results folders and experiment specific files.
    output_base_dir: str
        Directory to which all config files and results folders are saved.
    job_parameters: Dict[str, Any]
        Dictionary of parameters for the job array command that are handled by the JobArrayModel.
    runner_parameters: Dict[str, List[Any]]
        Dictionary containing the parameters grid submitted to the runner.
    """

    job_prefix: str
    runner: str
    output_base_dir: str
    job_parameters: JobArrayModel
    runner_parameters: Dict[str, List[Any]]

    @validator("output_base_dir")
    def output_base_dir_is_dir(cls, v):
        """
        Validate if output_base_dir is an existing directory.
        """
        if not os.path.isdir(v):
            raise ValueError(f'"{v}" is not a directory.')
        elif not v.endswith(os.path.sep):
            v += os.path.sep

        return v

    @validator("runner_parameters")
    def data_in_runner_parameters_and_file_or_path(cls, v):
        """
        Validate if "data" key is in runner_parameters and if it is either file or directory.
        """
        # check if runner_parameters contains data key
        assert "data" in v.keys()

        # check if all paths in "data" are existing files or directories
        for i, f in enumerate(v["data"]):
            if not (os.path.isfile(f) or os.path.isdir(f)):
                raise ValueError(f'"{f}" is not a file/directory.')
            else:
                if os.path.isdir(f) and not f.endswith(os.path.sep):
                    v["data"][i] = f + os.path.sep
        return v

    @validator("runner")
    def runner_is_file(cls, v):
        """
        Validate if "runner" is an existing file.
        """
        if not os.path.isfile(v):
            raise ValueError('"runner" is not a file.')
        return v


def _validation_func(params_path: Union[str, os.PathLike]) -> ConfigModel:
    with open(params_path, "r") as f:
        parameters = json.load(f)
    validated_parameters = ConfigModel(**parameters)
    return validated_parameters
