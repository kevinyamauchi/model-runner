import argparse
import json


def _validation_func(params):
    with open(params) as f:
        validated_parameters = json.load(f)
    return validated_parameters


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("params", help="path to the job params file", type=str)
    args = parser.parse_args()

    return args


def main():
    args = _parse_args()
    print(args)
