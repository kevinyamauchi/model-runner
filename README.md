# model-runner
**model-runner** is a Python-based CLI to submit hyper-parameter optimization (i.e. grid-search) jobs to the [LSF batch system](https://www.bsc.es/support/LSF/old-9.1.1/lsf_programmer/index.htm?batch_programmer_lsf.html~main). model-runner requires a `.json` config as input and validates the content of the config to prevent common errors such as non-existent files or incorrectly formatted LSF batch submissions parameters.

## Installation
model-runner was tested on ETH Zurich's EULER cluster (`IBM Spectrum LSF Standard 10.1.0.7`) and may not work on other clusters or lsf versions.

1) clone the repository

    ```bash
    git clone https://github.com/kevinyamauchi/model-runner
    ```

2) Navigate to the cloned directory

    ```bash
    cd model-runner
    ```

3) We recommend using a virtual environment. If you are using anaconda, you can use the following.

    ```bash
    conda create -n model-runner python=3.8
    ```

4) Activate your virtual environment, after it has been created. NOTE: Make sure the dependencies for your
training routine (i.e. `runner`) are installed.

    ```bash
    conda activate model-runner
    ```

5) Install `model-runner` in editable mode with the development dependencies.

    1) as a user

        ```bash
        pip install .
        ```
    2) as a developer (in editable mode with development dependencies and pre-commit hooks)
 
        ```bash
        pip install -e ".[dev]"
        pre-commit install
        ```

## Usage
1) Activate the virtual environment you installed model-runner to. To stay consistent with the above installation

    ```bash
    conda activate model-runner
    ```

2) Write your `.json` config file following the [config example](./examples/config_example.json). Our example config `config_example.json` contains the following parameters

    1) `job_parameters`: Dictionary containing the 
        1) (optional)`gpu_type`: Type of GPU that is accepted by bsub -R "select[gpu_model0=={gpu_type}]". See
        this [list of accepted GPUs](https://scicomp.ethz.ch/wiki/Getting_started_with_GPUs#Available_GPU_node_types). If not specified, the job will be run on CPU.

        2) `logfile_dir`: Path to directory to which lsf output files are saved.

        3) `memory`: Amount of memory requested per processor core. Corresponds to `bsub -R "rusage[mem={memory}]"`.

        4) (optional)`ngpus`: Number of GPUs of `gpu_type` requested. Corresponds to `bsub -R "rusage[ngpus_excl_p={ngpus}]"` and requires `gpu_type` to be specified.

        5) njobs_parallel: Number of jobs (i.e. hyper-parameter combinations) the model-runner will submit in parallel.

        6) `processor_cores`: Number of processor cores requested for a single job. Corresponds to `bsub -n {processor_cores}`.

        7) `run_time`: The time resources on the compute note are reservered for a single job. Corresponds to `bsub -W {run_time}`.

        8) `scratch`: Amount of local scratch requested per processor core. Corresponds to `bsub -R "rusage[scratch={scratch}]"`.

    2) `job_prefix`: Prefix that precedes all results folders and experiment specific files.

    3) `output_base_dir`: Directory to which all config files and results folders are saved.

    4) `runner`: Path to the file that trains your model.

    5) `runner_parameters`: Dictionary containing the parameters grid submitted to the runner.
        1) `data`: a list of paths to your data set file or directory (whatever your `runner` accepts as input
        data). **Note:** `runner` has to accept input data via `{runner} --data {data-path}`.

        2) `{parameter_placeholder}`: You can submit as many parameters as your `runner` accepts input arguments (besides `data`). You just have to make sure that `{parameter_placeholder}` matches an input argument of `runner` and the values of `{parameter_placeholder}` are wrapped in a list. Checkout the [config example](./examples/config_example.json) for an illustrative example.
          1) If the `type()` of the `parameter_placeholder` value is `bool` (see `augment` key in example
          config) `True` corresponds to adding the `--parameter_placeholder` flag (i.e. `python my_runner.py --parameter_placeholder`). `False` corresponds to
          omitting the flag from the `runner` call (i.e. `python my_runner.py`). NOTE: Beware of inverted logic if parser argument uses `action=store_false`.

3) Submit the hyper-parameter optimization

```bash
model_runner --params my_config.json
```


