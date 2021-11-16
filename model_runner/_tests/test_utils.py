import json
import os

from model_runner.utils import (
    _create_runner_param,
    _create_runner_params,
    _write_job_array,
    _write_runner_params,
)
from model_runner.validator import ConfigModel


def test_create_runner_param():
    param_names = ["batch_size", "learning_rate"]
    param_values = [10, 1]
    job_prefix = "test_job"
    runner = "runner.py"
    job_index = 1
    output_base_dir = "./output"
    params = _create_runner_param(
        param_names,
        param_values,
        job_prefix=job_prefix,
        runner=runner,
        output_base_dir=output_base_dir,
        job_index=job_index,
    )

    expected_params = {
        "runner": runner,
        "job_prefix": job_prefix,
        "job_index": job_index,
        "output_base_dir": output_base_dir,
        "batch_size": 10,
        "learning_rate": 1,
    }
    assert params == expected_params


def test_create_runner_params():
    params = {
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }
    job_prefix = "test_job"
    runner = "runner.py"
    output_base_dir = "./output"
    runner_params = _create_runner_params(
        params, job_prefix=job_prefix, runner=runner, output_base_dir=output_base_dir
    )
    runner_param_combinations = [
        (
            v["runner"],
            v["job_prefix"],
            v["output_base_dir"],
            v["batch_size"],
            v["augment"],
        )
        for v in runner_params.values()
    ]

    expected_params = [
        (runner, job_prefix, output_base_dir, 0, True),
        (runner, job_prefix, output_base_dir, 0, False),
        (runner, job_prefix, output_base_dir, 10, True),
        (runner, job_prefix, output_base_dir, 10, False),
        (runner, job_prefix, output_base_dir, 20, True),
        (runner, job_prefix, output_base_dir, 20, False),
    ]

    assert len(runner_params) == 6
    assert set(expected_params) == set(runner_param_combinations)
    assert {1, 2, 3, 4, 5, 6} == set(runner_params.keys())


def test_write_runner_params(tmp_path_factory):
    job_prefix = "test_job"
    runner = tmp_path_factory.mktemp("data") / "myfile"
    runner.touch()
    runner_path = runner.as_posix()
    output_base_dir = tmp_path_factory._basetemp.as_posix()

    params = {
        "data": [tmp_path_factory._basetemp.as_posix()],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }
    config = {
        "runner": runner_path,
        "output_base_dir": output_base_dir,
        "job_prefix": job_prefix,
        "runner_parameters": params,
        "job_parameters": {
            "gpu_type": "TITANRTX",
            "logfile_dir": tmp_path_factory._basetemp.as_posix(),
            "memory": 4000,
            "ngpus": 2,
            "njobs_parallel": 4,
            "processor_cores": 16,
            "run_time": "3:00",
            "scratch": 4000,
        },
    }
    config_model = ConfigModel(**config)

    output_path = os.path.join(tmp_path_factory._basetemp.as_posix(), "test.json")
    _write_runner_params(config_model, output_path)

    with open(output_path, "r") as f_json:
        runner_params = json.load(f_json)
    runner_param_combinations = [
        (
            v["runner"],
            v["job_prefix"],
            v["output_base_dir"],
            v["batch_size"],
            v["augment"],
        )
        for v in runner_params.values()
    ]
    # we expect the path sep to be added to the end of the base dir path
    validated_output_base_dir = output_base_dir + os.path.sep

    expected_params = [
        (runner_path, job_prefix, validated_output_base_dir, 0, True),
        (runner_path, job_prefix, validated_output_base_dir, 0, False),
        (runner_path, job_prefix, validated_output_base_dir, 10, True),
        (runner_path, job_prefix, validated_output_base_dir, 10, False),
        (runner_path, job_prefix, validated_output_base_dir, 20, True),
        (runner_path, job_prefix, validated_output_base_dir, 20, False),
    ]

    assert len(runner_params) == 6
    assert set(expected_params) == set(runner_param_combinations)
    assert {"1", "2", "3", "4", "5", "6"} == set(runner_params.keys())


def test_write_job_array(tmp_path_factory, base_config):
    runner_params_path = os.path.join(
        tmp_path_factory._basetemp.as_posix(), "test.json"
    )
    logfile_dir = os.path.join(tmp_path_factory._basetemp.as_posix(), "my_experiment")

    config_model = ConfigModel(**base_config)
    _write_runner_params(config_model, runner_params_path)

    job_array_command = _write_job_array(config_model, runner_params_path)
    expected_command = 'bsub -J "my_experiment[1-12]%4"'
    expected_command += f' -o "{logfile_dir}%I"'
    expected_command += ' -W "180"'
    expected_command += ' -n "16"'
    expected_command += ' -R "rusage[scratch=4000, mem=4000, ngpus_excl_p=2]"'
    expected_command += ' -R "select[gpu_model0==TITANRTX]"'
    expected_command += (
        f' "model_dispatcher --job_id \\$LSB_JOBINDEX --params {runner_params_path}"'
    )

    assert expected_command == job_array_command
