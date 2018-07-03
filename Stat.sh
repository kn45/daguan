#!/bin/bash

data_raw=data_all/train_set.csv
data_all=data_all/data_all.tsv

cat $data_raw | awk -F',' '{print $4}' | uniq | sort | uniq > data_all/stat_clz
cat $data_raw | awk -F',' '{print $2}' | tr ' ' '\n' | sort | uniq > data_all/stat_char
cat $data_raw | awk -F',' '{print $3}' | tr ' ' '\n' | sort | uniq > data_all/stat_word
