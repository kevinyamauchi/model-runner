import os

import pytest
from pydantic import ValidationError

from model_runner.validator.validator_utils import ConfigModel


@pytest.fixture(scope="session")
def base_config(tmp_path_factory):
    my_file = tmp_path_factory.mktemp("data") / "myfile"
    my_file.touch()

    config = {
        "job_prefix": "my_experiment",
        "runner_parameters": {
            "data": [tmp_path_factory._basetemp.as_posix()],
            "augment": [True, False],
            "batch_size": [2, 16, 32],
            "lr": [5e-05, 0.001],
        },
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
        "runner": my_file.as_posix(),
        "output_base_dir": tmp_path_factory._basetemp.as_posix(),
    }

    return config


def test_good_config(base_config):
    config = ConfigModel(**base_config)

    # test some specific parameters
    assert (
        type(config.dict()["job_prefix"]) == str
    ), '"job_prefix" should be of type str.'
    assert (
        type(config.dict()["job_parameters"]["run_time"]) == int
    ), '"run_time" should be of type int.'
    assert config.dict()["job_parameters"]["logfile_dir"].endswith(
        "/"
    ), '"logfile_dir" does not end with "/".'
    assert os.path.isdir(
        config.dict()["output_base_dir"]
    ), '"output_base_dir" is not a directory'


def test_bad_configs(base_config):
    # test gpu_type
    bad_config = base_config.copy()
    bad_config["job_parameters"].pop("gpu_type")
    bad_config["job_parameters"]["gpu_type"] = "Titanium"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test run_time
    bad_config = base_config.copy()
    bad_config["job_parameters"].pop("run_time")
    bad_config["job_parameters"]["run_time"] = "3:120"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test data
    bad_config = base_config.copy()
    bad_config["runner_parameters"].pop("data")

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    bad_config["runner_parameters"]["data"] = ["/some/bad/path"]

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test runner
    bad_config = base_config.copy()
    bad_config.pop("runner")
    bad_config["runner"] = "/non/existant/file"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)
