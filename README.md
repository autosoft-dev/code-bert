[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
![](build_badges/macpass.svg)
![](build_badges/linuxpass.svg)
![](build_badges/windowsfail.svg)
# code-bert

codeBERT is a package to **automatically check if your code documentation is up-to-date**. codeBERT currently works for Python code. 

*If you are using the source distribution the present version is available for Linux and Mac only. We are working on the Windows release. Please hang on*


This is [CodistAI](https://codist-ai.com/) open source version to easily use the fine tuned model based on our open source MLM code model [codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2)

[codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2) is a RoBERTa model, trained using Hugging Face Transformer library and then we have fine tuned the model on the task of predicting the following - 


## 🏆 code-bert output

Given a function `f` and a doc string `d` a code-bert predicts whether `f` and `d` are matching or not (meaning, whether they represent the same concept or not)

A report lists out all the functions where docsting does not matchn as follow:

```
 ======== Analysing test_files/inner_dir/test_code_get.py =========

>>> Function "get_file" with Dcostring """opens a url"""
>>> Do they match?
No

```


## code-bert local setup 

**The entire code base is built and abvailble for Python3.6+**

We have provided very easy to use CLI commands to achieve all these, and at scale. Let's go through that step by step

**We strongly recommend using a virtual environment for the followinsg steps** 

1. First clone this repo - `git clone https://github.com/autosoft-dev/code-bert.git && cd code-bert`

2. (Assuming you have the virtualenv activated) Then do `pip install -r requirements.txt`

3. Then install the package with `pip install -e .`

4. First step is to download and set up the model. If the above steps are done properly then there is command for doing this `download_model`

5. The model is almost 1.7G in total, so it may take a bit of time before it finishes.

6. Once this is done, you are ready to analyze code. For that we have a CLI option also. Details of that in the following section

-----------

You can run the following command to analyze one file or a directory containing a bunch of files

```
usage: run_pipeline [-h] [-f FILE_NAME] [-r RECURSIVE] [-m]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_NAME, --file_name FILE_NAME
                        The name of the file you want to run the pipeline on
  -r RECURSIVE, --recursive RECURSIVE
                        Put the directory if you want to run recursively
  -m, --show_match      Shall we show the matches? (Default false)
```

## code-bert Docker

It has been request by our users and here it is! You will not need to go through any painful setup process at all. We have Dockerized the entire thing for you. Here are the steps to use it. 

- Pull the image `docker pull codistai/codebert`

- Assuming that you have a bunch of files to be analyzed under `test_files` in your present working directory, run this command - `docker run -v "$(pwd)"/test_files:/usr/src/app/test_files -it codistai/codebert run_pipeline -r test_files`

- If you wish to analyze any other directory, simply change the mounting option in the `docker run` command (the path after `-v` the format should be `full/local/path:/usr/src/app/<mount_dir_name>`) and also mention the same `<mount_dir_name>` after the `run_pipeline` command.



## 🎮 code-bert example

SLet's say you have a directory called `test_files` with some python files in it. Here is how to run the analysis: 

`run_pipeline  -r test_files`

The algorithm will take one file at a time to analyze recursively on the whole directory and prompt out a report of not matching function-docstring pairs.

```
 ======== Analysing test_files/test_code_add.py =========


 ======== Analysing test_files/inner_dir/test_code_get.py =========
>>> Function "get_file" with Dcostring """opens a url"""
>>> Do they match?
No
******************************************************************
```


You can optionally pass the `--show_match` flag like so `run_pipeline -r test_files --show_match` to prompt out both match and mismatching function-docstring pairs.

```
 ======== Analysing test_files/test_code_add.py =========


>>> Function "add" with Dcostring """sums two numbers and returns the result"""
>>> Do they match?
Yes
******************************************************************
>>> Function "return_all_even" with Dcostring """numbers that are not really odd"""
>>> Do they match?
Yes
******************************************************************

 ======== Analysing test_files/inner_dir/test_code_get.py =========


>>> Function "get_file" with Dcostring """opens a url"""
>>> Do they match?
No
******************************************************************
```



## 💡 code-bert logic

Let's consider the following code

```python
from pathlib import Path

def get_file(filename):
    """
    opens a url
    """
    if not Path(filename).is_file():
        return None
    return open(filename, "rb")

```
1. Mine souce code to get function-docstring pairs using [tree-hugger](https://github.com/autosoft-dev/tree-hugger)
2. Prep for functions and docstring data to fit input format expected by [codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2) model.
- **Function** - `def get file ( filename ) : indent if not path ( filename ) . is file ( ) : indent return none dedent return open ( filename , "rb" ) dedent`

- **Doc String** - `opens a url`

3. Run the model 
```python
match, confidence = model(function, docstring)
```


Stay tuned! 
