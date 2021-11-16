import json
import os

from model_runner.utils import (
    _create_runner_param,
    _create_runner_params,
    _write_job_array,
    _write_runner_params,
)


def test_create_runner_param():
    param_names = ["runner", "batch_size", "learning_rate"]
    param_values = ["hello.py", 10, 1]
    params = _create_runner_param(param_names, param_values)

    expected_params = {"runner": "hello.py", "batch_size": 10, "learning_rate": 1}
    assert params == expected_params


def test_create_runner_params():
    params = {
        "runner": ["hello.py"],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }
    runner_params = _create_runner_params(params)
    runner_param_combinations = [
        (v["runner"], v["batch_size"], v["augment"]) for v in runner_params.values()
    ]

    expected_params = [
        ("hello.py", 0, True),
        ("hello.py", 0, False),
        ("hello.py", 10, True),
        ("hello.py", 10, False),
        ("hello.py", 20, True),
        ("hello.py", 20, False),
    ]

    assert len(runner_params) == 6
    assert set(expected_params) == set(runner_param_combinations)
    assert {1, 2, 3, 4, 5, 6} == set(runner_params.keys())


def test_write_runner_params(tmp_path):
    output_path = os.path.join(tmp_path, "test.json")
    params = {
        "runner": ["hello.py"],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }

    _write_runner_params(params, output_path)

    # test if params was correctly saved
    with open(output_path, "r") as f:
        runner_params = json.load(f)

    runner_param_combinations = [
        (v["runner"], v["batch_size"], v["augment"]) for v in runner_params.values()
    ]

    expected_params = [
        ("hello.py", 0, True),
        ("hello.py", 0, False),
        ("hello.py", 10, True),
        ("hello.py", 10, False),
        ("hello.py", 20, True),
        ("hello.py", 20, False),
    ]

    assert len(runner_params) == 6
    assert set(expected_params) == set(runner_param_combinations)
    assert {"1", "2", "3", "4", "5", "6"} == set(runner_params.keys())


def test_write_job_array(tmp_path):
    job_prefix = "test_"
    njobs_parallel = 4
    runner_params_path = os.path.join(tmp_path, "test.json")

    params = {
        "runner": ["hello.py"],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }

    _write_runner_params(params, runner_params_path)

    job_array_command = _write_job_array(runner_params_path, job_prefix, njobs_parallel)
    expected_command = f'bsub -J "test_[1-6]%4 model_dispatcher --job_id \\$LSB_JOBINDEX --params {runner_params_path}"'

    assert expected_command == job_array_command
