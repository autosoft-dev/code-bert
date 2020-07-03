# code-bert

codeBERT is a package to **automatically review you code documentation**. codeBERT currently works for Python code. 

*code-bert present version is available for Linux and Mac only. We are working on the Windows release. Please hang on*


🔨 Given a function body `f` as a string of code tokens (including special tokens such as `indent` and `dedent`) and a doc string `d` as a string of Natual Language tokens. Predict whether `f` and `d` are assciated or not (meaning, whether they represent the same concept or not)

This is [CodistAI](https://codist-ai.com/) open source version to easily use the fine tuned model based on our open source MLM code model [codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2)

[codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2) is a RoBERTa model, trained using Hugging Face Transformer library and then we have fine tuned the model on the task of predicting the following - 



## An example

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

💡 Using our another open source library [tree-hugger](https://github.com/autosoft-dev/tree-hugger) it is fairly trivial to get the code and separate out the function body and the docstring with a single API call. 

We can use then, the [`process_code`](https://github.com/autosoft-dev/code-bert/blob/2dd35f16fa2cdb96f75e21bb0a9393aa3164d885/code_bert/core/data_reader.py#L136) method from this prsent repo to process the code lines in the proper format as [codeBERT-small-v2](https://huggingface.co/codistai/codeBERT-small-v2) would want.

Doing the above two steps properly would produce something like the following

- **Function** - `def get file ( filename ) : indent if not path ( filename ) . is file ( ) : indent return none dedent return open ( filename , "rb" ) dedent`

- **Doc String** - `opens a url`

Ideally then we need some model to run the following Pseudocode

```python
match, confidence = model(function, docstring)
```

And ideally, in this case, the match should be `False`

## code-bert CLI

**The entire code base is built and abvailble for Python3.6+**

We have provided very easy to use CLI commands to achieve all these, and at scale. Let's go through that step by step

**We strongly recommend using a virtual environment for the followinsg steps** 

1. First clone this repo - `git clone https://github.com/autosoft-dev/code-bert.git`

2. (Assuming you have the virtualenv activated) Then do `pip install -r requirements.txt`

3. Then install the package with `pip install -e .`

4. First step is to download and set up the model. If the above steps are done properly then there is command for doing this `download_model`

5. The model is almost 1.7G in total, so it may take a bit of time before it finishes.

6. Once this is done, you are ready to analyze code. For that we have a CLI option also. Details of that in the following section

-----------

Assuming that model is downloaded and ready, you can run the following command to analyze one file or a directory containing a bunch of files

```
usage: run_pipeline [-h] [-f FILE_NAME] [-r RECURSIVE]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE_NAME, --file_name FILE_NAME
                        The name of the file you want to run the pipeline on
  -r RECURSIVE, --recursive RECURSIVE
                        Put the directory if you want to run recursively
```

So, let's say you have a directory called `test_files` with some python files in it. This is how you can analyze them

`run_pipeline  -r test_files`

A prompt will appear to confirm the model location. Once you confirm that then the algorithm will take one file at a time and analyze that, recursively on the whole directory. 

🏆 It should produce a report like the following - 


```
 ======== Analysing test_files/test_code_add.py =========


Function "add" with Dcostring """sums two numbers and returns the result"""
Do they match?
Yes
******************************************************************
Function "return_all_even" with Dcostring """numbers that are not really odd"""
Do they match?
Yes
******************************************************************

 ======== Analysing test_files/inner_dir/test_code_get.py =========


Function "get_file" with Dcostring """opens a url"""
Do they match?
No
******************************************************************
```

Stay tuned! 
