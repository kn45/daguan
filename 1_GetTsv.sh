#!/bin/bash

data_raw=data_all/train_set.csv
data_all=data_all/data_all.tsv

pred_raw=data_all/test_set.csv
data_pred=data_pred/data_pred.tsv

cat $data_raw | awk -F',' '{print $4"\t"$2"\t"$3}' > $data_all
cat $pred_raw | awk -F',' '{print "0\t"$2"\t"$3}' > $data_pred
