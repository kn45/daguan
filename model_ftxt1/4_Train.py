#!/usr/bin/env python

import fasttext
import sys

# model related
MODE = 'supervised'
# IO related
INPUT_FILE = 'feat_train/trnvld_feature.ssv'
MODEL_FILE = 'mdl_fasttext_' + MODE

model = fasttext.supervised(
    input_file=INPUT_FILE,
    output=MODEL_FILE,
    min_count=5,
    word_ngrams=2,
    bucket=2000000,
    minn=1,
    maxn=15,
    dim=256,
    epoch=70,
    neg=10,
    thread=6,
    loss='ns',
    silent=0)
