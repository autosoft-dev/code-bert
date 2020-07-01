# Sources - https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests
# And - https://stackoverflow.com/questions/16694907/download-large-file-in-python-with-requests
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

from tqdm import tqdm
import requests

BASE_URL = "https://codistai-code-doc-association-model.s3.amazonaws.com"


def _download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        block_size = 1024 #1 Kbyte
        t=tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(block_size): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                t.update(len(chunk))
                f.write(chunk)
    return local_filename


def download_file(model_file_name="Model.zip"):
    print("Downloading =========")
    local_file_name = _download_file(f"{BASE_URL}/{model_file_name}")
    
    print(f"File is saved as {local_file_name}")
    
    print("Unzipping ==========")
    if Path("Model").exists():
        shutil.rmtree("Model")

    with ZipFile(local_file_name) as zip:
        zip.extractall()

    os.remove(local_file_name)


def main():
    download_file()


if __name__ == "__main__":
    main()