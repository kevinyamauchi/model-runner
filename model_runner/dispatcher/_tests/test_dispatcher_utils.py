import pytest

from model_runner.dispatcher.dispatcher_utils import create_run_command


def test_create_run_command():
    params = {
        "runner": "test.py",
        "data": "path_to_data",
        "batch_size": 1,
        "learning_rate": 0.01,
    }
    run_command = create_run_command(params)

    expected_command = (
        "python test.py --data path_to_data --batch_size 1 --learning_rate 0.01"
    )
    assert run_command == expected_command


def test_create_run_command_errors():
    params_no_runner = {"data": "path_to_data", "batch_size": 1, "learning_rate": 0.01}
    with pytest.raises(KeyError):
        _ = create_run_command(params_no_runner)

    params_bad_runner = {
        "runner": 5,
        "data": "path_to_data",
        "batch_size": 1,
        "learning_rate": 0.01,
    }
    with pytest.raises(TypeError):
        _ = create_run_command(params_bad_runner)
