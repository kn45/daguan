#!/bin/bash

# Build feature using various ways from tsv file
# tsv -> feature

data_trnvld=../data_train/data_trnvld.tsv
data_train=../data_train/data_train.tsv
data_valid=../data_train/data_valid.tsv
data_test=../data_test/data_test.tsv

feat_trnvld=feat_train/trnvld_feature.ssv
feat_train=feat_train/train_feature.ssv
feat_valid=feat_train/valid_feature.ssv
feat_test=feat_test/test_feature.ssv


mkdir -p feat_train
mkdir -p feat_test


cat $data_trnvld | awk -F'\t' '{print "__label__"$1-1" "$3}' > $feat_trnvld

cat $data_test   | awk -F'\t' '{print "__label__"$1-1" "$3}' > $feat_test
