import os

from tree_hugger.core import PythonParser
from .data_reader import process_code


def iter_dir(dir_name):
    for root, _ ,f_names in os.walk(dir_name):
        for f in f_names:
            yield os.path.join(root, f)


class FileParser(object):

    def __init__(self, lib_location, query_file_location):
        self.pp = PythonParser(lib_location, query_file_location)
    
    def _combine_lines(self, logical_lines):
        c = " ".join(logical_lines)
        c = c.split()
        return " ".join(c) if len(c) < 256 else " ".join(c[:256])

    
    def parse_file_and_get_data(self, file_path):
        if not self.pp.parse_file(file_path):
            raise Exception(f"\n\nCould not parse file {file_path}")
        func_name_and_doc_str = self.pp.get_all_function_docstrings(strip_quotes=True)
        func_name_and_body = self.pp.get_all_function_bodies(strip_docstr=True)
        
        for fname, docstr in func_name_and_doc_str.items():
            if func_name_and_body.get(fname):
                func_body, _ = func_name_and_body[fname]
                logical_lines = process_code(func_body)
                combined_lines = self._combine_lines(logical_lines)
                yield fname, combined_lines, docstr.split("\n")[0]