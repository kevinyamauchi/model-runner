# model-runner
Runner for torch models

## Installation
### Development
First, clone the repository

```bash
git clone https://github.com/kevinyamauchi/model-runner
```

Navigate to the cloned directory

```bash
cd model-runner
```

We recommend using a virtual environment. If you are using anaconda, you can use the following.

```bash
conda create -n model-runner python=3.8
```

Activate your virtual environment, after your it has been created.

```bash
conda activate model-runner
```

Install `model-runner` in editable mode with the development dependencies.

```bash
pip install -e ".[dev]"
```

Finally, install the pre-commit hooks. We use these to automatically format and lint each commit.

```bash
pre-commit install
```
