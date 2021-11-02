import pytest
from pydantic import ValidationError

from model_runner.validator.validator_utils import ConfigModel


@pytest.fixture(scope="session")
def base_config(tmp_path_factory):
    my_file = tmp_path_factory.mktemp("data") / "myfile"
    my_file.touch()

    config = {
        "data": tmp_path_factory._basetemp,
        "hyperparameters": {
            "augment": [True, False],
            "batch_size": [2, 16, 32],
            "lr": [5e-05, 0.001],
        },
        "job_array": {
            "gpu_type": "TITANRTX",
            "logfile_name_template": "my_job",
            "memory": 4000,
            "ngpus": 2,
            "njobs": 20,
            "njobs_parallel": 4,
            "processor_cores": 16,
            "run_time": "3:00",
            "scratch": 4000,
        },
        "runner": my_file,
    }

    return config


def test_good_config(base_config):
    try:
        _ = ConfigModel(**base_config)
    except ValidationError as e:
        print(e)


def test_bad_configs(base_config):
    # test gpu_type
    bad_config = base_config.copy()
    bad_config["job_array"]["gpu_type"] = "Titanium"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test run_time
    bad_config = base_config.copy()
    bad_config["job_array"]["run_time"] = "3:120"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test data
    bad_config = base_config.copy()
    bad_config["data"] = "/some/bad/path"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)

    # test runner
    bad_config = base_config.copy()
    bad_config["runner"] = "/non/existant/file"

    with pytest.raises(ValidationError):
        _ = ConfigModel(**bad_config)
