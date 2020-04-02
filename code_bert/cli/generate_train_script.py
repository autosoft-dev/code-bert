import argparse
import os
from pathlib import Path
import shutil
import json

from invoke import run
from tokenizers import ByteLevelBPETokenizer

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--vocab', dest='vocab', action='store_true')
parser.add_argument('--no-vocab', dest='vocab', action='store_false')
parser.set_defaults(vocab=False)

parser.add_argument('--smalldata', dest='smalldata', action='store_true')
parser.add_argument('--no-smalldata', dest='smalldata', action='store_false')
parser.set_defaults(smalldata=True)



def _create_train_files_and_regenerate_vocab():
    print("pass")
    r = run("split -l1000000 train.txt --verbose")
    if r.ok:
        print("Train splits generated")
    if r.ok:
        try:
            shutil.rmtree("td")
        except FileNotFoundError:
            pass
        os.mkdir("td")
        r = run("mv xaa td/xaa.txt | mv xab td/xbb.txt | mv xac td/xac.txt | mv xad td/xad.txt | mv xae td/xae.txt | mv xaf td/xaf.txt")
        if r.ok:
            paths = [str(x) for x in Path(".").glob("td/*.txt")]
            tokenizer = ByteLevelBPETokenizer()

            # Customize training
            tokenizer.train(files=paths, vocab_size=52_000, min_frequency=2, special_tokens=[
                "<s>",
                "<pad>",
                "</s>",
                "<unk>",
                "<mask>",
                "<indent>",
                "<dedent>",
                "<newline>",
                "<foreignchars>"
            ])
            try:
                shutil.rmtree("codeBERT")
            except FileNotFoundError:
                pass
            os.mkdir("codeBERT")
            tokenizer.save("codeBERT")


def generate_train_command(args):
    if args.vocab:
        _create_train_files_and_regenerate_vocab()
    config = {
        "architectures": [
            "RobertaForMaskedLM"
        ],
        "attention_probs_dropout_prob": 0.1,
        "hidden_act": "gelu",
        "hidden_dropout_prob": 0.1,
        "hidden_size": 768,
        "initializer_range": 0.02,
        "intermediate_size": 3072,
        "layer_norm_eps": 1e-05,
        "max_position_embeddings": 1024,
        "model_type": "roberta",
        "num_attention_heads": 12,
        "num_hidden_layers": 6,
        "type_vocab_size": 1,
        "vocab_size": 52000
    }
    with open("codeBERT/config.json", 'w') as fp:
        json.dump(config, fp)

    tokenizer_config = {
        "max_len": 1024
    }
    with open("codeBERT/tokenizer_config.json", 'w') as fp:
        json.dump(tokenizer_config, fp)

    train_file = "train.txt"
    eval_file = "valid.txt"
    
    if args.smalldata:
        r = run("rm -f small_eval.txt small_train.txt")
        if r.ok:
            r = run("head -1000000 train.txt > small_train.txt")
            r = run("tail -10000 train.txt > small_eval.txt")
            if r.ok:
                train_file = "small_train.txt"
                eval_file = "small_eval.txt"
    r = run("rm -rf codeBERT-small-v1 runs")
    cmd ="""
        CUDA_LAUNCH_BLOCKING=1 python run_language_modeling.py
        --train_data_file {}
        --eval_data_file {}
        --output_dir ./codeBERT-small-v1
            --model_type roberta
            --mlm
            --config_name ./codeBERT
            --tokenizer_name ./codeBERT
            --do_train
            --do_eval
            --line_by_line
            --learning_rate 1e-4
            --num_train_epochs 1
            --save_total_limit 2
            --save_steps 2000
            --per_gpu_train_batch_size 4
            --gradient_accumulation_steps 4
            --seed 42 > train.log &
        """.format(train_file, eval_file).replace("\n", " ")
    return cmd


def main():
    args = parser.parse_args()
    cmd = generate_train_command(args)
    print(cmd)
