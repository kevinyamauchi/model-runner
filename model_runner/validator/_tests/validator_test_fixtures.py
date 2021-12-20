import pytest


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
            "gpu_type": "NVIDIATITANRTX",
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
