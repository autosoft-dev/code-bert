import argparse
import os
from pathlib import Path
import json

from invoke import run

from code_bert.core.data_reader import process_code

RAW_TRAIN_FILE_NAME = "train.txt"
RAW_VALIDATION_FILE_NAME = "valid.txt"

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("--data_type", type=str)
parser.add_argument("--main_path", type=str, help="Give the main path to the data dir.")
parser.add_argument("--training_data_path", type=str)
parser.add_argument("--validation_data_path", type=str)


def code_search_net_data(args):
    dirs = list(os.listdir(args.main_path))
    for d in dirs:
        for x in Path(f"{args.main_path}/{d}").glob("*.gz"):
            r = run(f"gzip -d {x}", hide=True, warn=True)
            print(f"{x} extration is OKay: {r.ok}")
    
    train_dirs = [x for x in dirs if x != "valid"]
    valid_dirs = [x for x in dirs if x == "valid"]

    with open(RAW_TRAIN_FILE_NAME, "a") as f:
        for d in train_dirs:
            for x in Path(f"{args.main_path}/{d}").glob("*.jsonl"):
                print("Processing {x}")
                with open(f"{x}", "r") as fd:
                    code_lines = fd.readlines()
                for line in code_lines:
                    to_write = process_code(json.loads(line)["code"])
                    if to_write:
                        try:
                            print(to_write, file=f)
                        except UnicodeEncodeError:
                            pass

    with open(RAW_VALIDATION_FILE_NAME, "a") as f:
        for d in valid_dirs:
            for x in Path(f"{args.main_path}/{d}").glob("*.jsonl"):
                with open(f"{x}", "r") as fd:
                    code_lines = fd.readlines()
                for line in code_lines:
                    to_write = process_code(json.loads(line)["code"])
                    if to_write:
                        try:
                            print(to_write, file=f)
                        except UnicodeEncodeError:
                            pass


def main():
    args = parser.parse_args()
    if args.data_type == "code_search_net":
        code_search_net_data(args)
    else:
        print(f"{args.data_type} is not supported yet")
