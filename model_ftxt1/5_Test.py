#!/usr/bin/env python

import fasttext
import itertools
import sys
sys.path.append('../utils')
from dataproc import f1_multiclass

test_file = 'feat_test/test_feature.ssv'
test_res = 'res_test/res_test.tsv'
BATCH_SIZE = 256

mdl = fasttext.load_model('mdl_fasttext_supervised.bin')
with open(test_file) as fi, open(test_res, 'w') as fo:
    # label(__label__4), chars, words
    iter_cnt = 0
    feats_buff = []
    label_buff = []
    for line in fi:
        iter_cnt += 1
        flds = line.rstrip('\n').split(' ')
        test_label = flds[0][9:]
        test_feats = ' '.join(flds[1:])
        feats_buff.append(test_feats)
        label_buff.append(test_label)
        if iter_cnt % BATCH_SIZE != 0:
            continue
        pred_raws = mdl.predict(feats_buff, 1)
        for pred_raw, test_label in zip(pred_raws, label_buff):
            pred_label = pred_raw[0][9:]
            print(test_label, pred_label, file=fo, sep='\t')
        iter_cnt = 0
        feats_buff = []
        label_buff = []

with open(test_res) as f:
    data_test = [l.rstrip('\n').split('\t') for l in f.readlines()]
t_values = [l[0] for l in data_test]
p_values = [l[1] for l in data_test]
print(f1_multiclass(t_values, p_values))
