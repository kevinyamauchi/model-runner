import os

import pytest
from pydantic import ValidationError

from model_runner.validator.validator_utils import ConfigModel


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
        os.path.sep
    ), f'"logfile_dir" does not end with "{os.path.sep}".'
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
