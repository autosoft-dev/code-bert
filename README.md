# code-bert
BERT/RoBERTa kind of language representation model training and fine tuning

We have released the model [here](https://huggingface.co/codistai/codeBERT-small-v2)

However, this small python module serves as the pre-tokenization step needed for the tokenizer to deal with code.


```
from code_bert.core.data_reader

with open("test_files/test_code_get.py") as f:
    code = f.read()


process_code(code)
```

This will produce a result like this 

```
Out[4]:
['from pathlib import path',
 'def get file ( filename ) : indent',
 'if not path ( filename ) . is file ( ) : indent',
 'return none',
 'dedent return open ( filename , "rb" ) dedent']
```