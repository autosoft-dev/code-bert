import logging
import platform
from pathlib import Path
from argparse import ArgumentParser

from .utils import query_yes_no
from ..core.data_preparation import iter_dir, FileParser
from ..core.prediction import Prediction

LIBS = {"Linux": "libs/linux", "Darwin": "libs/darwin"}

logging.disable(logging.INFO)

is_python_file = lambda x: Path(x).suffix == ".py"


def _my_os():
    return platform.system()


def _run_model(file_path, file_parser, predictor):
    print(f"\n ======== Analysing {file_path} =========\n\n")
    for func_name, func_body, docstr in file_parser.parse_file_and_get_data(file_path):
        match, _ = predictor.predict(func_body, docstr)
        match_yes = "Yes" if bool(match) == True else "No"
        print(f'>>> Function "{func_name}" with Dcostring """{docstr}"""\n>>> Do they match?\n{match_yes}')
        print("******************************************************************")


def run_pipeline(args):
    if args.file_name and args.recursive:
        raise Exception("\n\nCan not mention both a single file and a directory.\n Either of them"
        )
    
    if not Path("Model").exists() or not Path("Model").is_dir():
        raise Exception("\n\nEither the Model directory does not exist or it is invalid")

    choice = query_yes_no("We believe that the model is at 'Model' directory. Shall we continue?")

    if choice:
        print("Loading model")
        predictor = Prediction("Model")
        print("Model loaded")
        os_version = _my_os()
        lib = LIBS.get(os_version)
        if not lib:
            raise Exception(f"\n\nYour version of OS {os_version} is not supported yet!")
        lib = f"{lib}/my-languages.so"
        query_file = "queries/queries.yml"

        fp = FileParser(lib, query_file)

        if args.recursive:
            for file_path in iter_dir(args.recursive):
                if is_python_file(file_path):
                    _run_model(file_path, fp, predictor)     
        else:
            if is_python_file(file_path):
                _run_model(file_path, fp, predictor)
    else:
        print("Bye Bye!")



def main():
    parser = ArgumentParser()
    parser.add_argument("-f", "--file_name", type=str, required=False, help="The name of the file you want to run the pipeline on")
    parser.add_argument("-r", "--recursive", required=False, help="Put the directory if you want to run recursively")

    args = parser.parse_args()
    run_pipeline(args)
