from typing import Any, Dict


def create_run_command(params: Dict[str, Any]) -> str:
    """Create the run command that will start the training/prediction.

    Parameters
    ----------
    params : Dict[str, Any]
        The parameters for the job. It must contain "runner", which is
        the path to the python script to run the job. All other key/values
        will be passed as arguments to the runner as "--key value"

    Returns
    -------
    job_command : str
        The command that will be executed on the command line.
    """
    try:
        runner = params.pop("runner")
        assert isinstance(runner, str)
    except KeyError:
        raise KeyError("params must contain the key 'runner'")
    except AssertionError:
        raise TypeError("runner should be a string")

    try:
        output_base_dir = params.pop("output_base_dir")
        assert isinstance(output_base_dir, str)
    except KeyError:
        raise KeyError("params must contain the key 'output_base_dir'")
    except AssertionError:
        raise TypeError("'output_base_dir' should be a string")

    try:
        job_index = params.pop("job_index")
        assert isinstance(job_index, int)
    except KeyError:
        raise KeyError("params must contain the key 'job_index'")
    except AssertionError:
        raise TypeError("'job_index' should be a string")

    try:
        job_prefix = params.pop("job_prefix")
        assert isinstance(job_prefix, str)
    except KeyError:
        raise KeyError("params must contain the key 'job_prefix'")
    except AssertionError:
        raise TypeError("'job_prefix' should be a string")

    job_command = f"python {runner}"
    params["output_base_dir"] = f"{output_base_dir}{job_prefix}{job_index}/"

    for k, v in params.items():
        if type(v) == bool:
            if v is True:
                job_command += f" --{k}"
            else:
                pass
        else:
            job_command += f" --{k} {v}"

    return job_command
