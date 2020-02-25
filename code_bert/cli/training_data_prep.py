import argparse
import os
from pathlib import Path

from invoke import run

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--main_path", type=str, help="Give the main path to the data dir.")
parser.add_argument("--training_data_path", type=str)
parser.add_argument("--validation_data_path", type=str)


def main():
    args = parser.parse_args()
    dirs = list(os.listdir(args.main_path))
    for d in dirs:
        for x in Path(f"{args.main_path}/{d}").glob("*.gz"):
            r = run(f"gzip -d {x}", hide=True, warn=True)
            print(f"{x} extration is OKay: {r.ok}")
