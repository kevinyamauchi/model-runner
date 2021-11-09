import json
import os

from model_runner.utils import (
    _create_job_array_params,
    _create_job_param,
    write_runner_params,
)


def test_create_job_param():
    param_names = ["runner", "batch_size", "learning_rate"]
    param_values = ["hello.py", 10, 1]
    params = _create_job_param(param_names, param_values)

    expected_params = {"runner": "hello.py", "batch_size": 10, "learning_rate": 1}
    assert params == expected_params


def test_create_job_array_params():
    params = {
        "runner": ["hello.py"],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }
    job_array_params = _create_job_array_params(params)
    job_array_param_combinations = [
        (v["runner"], v["batch_size"], v["augment"]) for v in job_array_params.values()
    ]

    expected_params = [
        ("hello.py", 0, True),
        ("hello.py", 0, False),
        ("hello.py", 10, True),
        ("hello.py", 10, False),
        ("hello.py", 20, True),
        ("hello.py", 20, False),
    ]

    assert len(job_array_params) == 6
    assert set(expected_params) == set(job_array_param_combinations)
    assert {1, 2, 3, 4, 5, 6} == set(job_array_params.keys())


def test_write_job_array_params(tmpdir):
    output_path = os.path.join(tmpdir, "test.json")

    params = {
        "runner": ["hello.py"],
        "batch_size": [0, 10, 20],
        "augment": [True, False],
    }

    write_runner_params(params, output_path)

    with open(output_path, "r") as f_json:
        job_array_params = json.load(f_json)
    job_array_param_combinations = [
        (v["runner"], v["batch_size"], v["augment"]) for v in job_array_params.values()
    ]

    expected_params = [
        ("hello.py", 0, True),
        ("hello.py", 0, False),
        ("hello.py", 10, True),
        ("hello.py", 10, False),
        ("hello.py", 20, True),
        ("hello.py", 20, False),
    ]

    assert len(job_array_params) == 6
    assert set(expected_params) == set(job_array_param_combinations)
    assert {"1", "2", "3", "4", "5", "6"} == set(job_array_params.keys())
