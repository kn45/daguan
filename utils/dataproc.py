# -*- coding=utf-8 -*-
from __future__ import print_function
import copy
import numpy as np
import sys
from operator import itemgetter


class DictTable(object):
    def __init__(self, dict_file=None, UNK=None):
        """dict file format:
        word '\t' index
        """
        self.table = {}
        self.rev_table = {}
        self.UNK = UNK
        self.update(dict_file)

    def update(self, dict_file):
        if isinstance(dict_file, basestring):
            with open(dict_file) as f:
                for line in f:
                    k, v = line.rstrip('\n').split('\t')
                    self.table[k] = int(v)
                    self.rev_table[int(v)] = k
                    if v == self.UNK:
                        sys.stderr.write('word index is conflict with UNK: ')
                        sys.stderr.write(k + ' ' + v + '\n')
        if isinstance(dict_file, dict):
            self.table = copy.deepcopy(dict_file)
            for k in dict_file:
                self.rev_table[dict_file[k]] = k
                if dict_file[k] == self.UNK:
                    sys.stderr.write('word index is conflict with UNK: ')
                    sys.stderr.write(str(k) + ' ' + str(v) + '\n')

    def lookup(self, words):
        ids = []
        for word in words:
            if word in self.table:
                ids.append(self.table[word])
            else:
                ids.append(self.UNK)
        return ids

    def lookup_rev(self, ids):
        ids = map(int, list(ids))
        words = []
        for idx in ids:
            if idx in self.rev_table:
                words.append(self.rev_table[idx])
            else:
                words.append(None)
        return words


class BinSpliter(object):
    def __init__(self):
        self.data = {}

    def load_bin(self, fname):
        with open(fname) as f:
            for ln in f:
                col_name, sps = ln.rstrip('\n').split('\t')
                sps = map(float, sps.split(' '))
                self.data[col_name] = sorted(sps)

    def save_bin(self, fname):
        with open(fname, 'w') as fo:
            for col in self.data:
                print(col, ' '.join(map(str, self.data[col])), sep='\t', file=fo)

    def add_bin(self, src, col_name, nbins):
        sorted_data = sorted(src)
        sps = []
        for i in range(nbins-1):  # nbins-1 spliters
            idx = int((i+1.)/nbins*len(src))
            sps.append(sorted_data[idx])
        self.data[col_name] = sps

    def find_bin(self, col, val):
        low_idx = -1
        up_idx = 0
        while True:
            if low_idx < 0:
                if val < self.data[col][up_idx]:
                    return up_idx
            elif up_idx == len(self.data[col]):
                return up_idx
            elif self.data[col][low_idx] <= val < self.data[col][up_idx]:
                return up_idx
            low_idx += 1
            up_idx += 1

    def find_onehot(self, col, val):
        res = [0] * (len(self.data[col]) + 1)
        res[self.find_bin(col, val)] = 1
        return res


class BatchReader(object):
    """Get batch data recurrently from a file.
    """
    def __init__(self, file_name, max_epoch=None):
        self.fname = file_name
        self.max_epoch = max_epoch
        self.nepoch = 0
        self.fp = None

    def __del__(self):
        if self.fp:
            self.fp.close()

    def get_batch(self, batch_size, out=None):
        if out is None:
            out = []
        if not self.fp:
            if (not self.max_epoch) or self.nepoch < self.max_epoch:
                # if max_epoch not set or num_epoch not reach the limit
                self.fp = open(self.fname)
                self.nepoch += 1
            else:  # reach max_epoch limit
                return out
        for line in self.fp:
            out.append(line.rstrip('\n'))
            if len(out) >= batch_size:
                break
        else:
            self.fp.close()
            self.fp = None
            return self.get_batch(batch_size, out)
        return out


def sparse2dense(ids, ndim):
    out = np.zeros((ndim), dtype=np.int32)
    for idx in ids:
        out[idx] = 1
    return out


def id2onehot(idx, ndim):
    out = np.zeros((ndim), dtype=np.int32)
    out[idx] = 1
    return out


def zero_padding(inp, seq_len):
    out = np.zeros((seq_len), dtype=np.int32)
    for i, v in enumerate(inp):
        if i >= seq_len:
            break
        out[i] = v
    return out


def draw_progress(iteration, total, pref='Progress:', suff='',
                  decimals=1, barlen=50):
    """Call in a loop to create terminal progress bar
    """
    formatStr = "{0:." + str(decimals) + "f}"
    pcts = formatStr.format(100 * (iteration / float(total)))
    filledlen = int(round(barlen * iteration / float(total)))
    bar = '█' * filledlen + '-' * (barlen - filledlen)
    out_str = '\r%s |%s| %s%s %s' % (pref, bar, pcts, '%', suff)
    out_str = '\x1b[0;34;40m' + out_str + '\x1b[0m'
    sys.stderr.write(out_str),
    if iteration == total:
        sys.stderr.write('\n')
    sys.stderr.flush()


def auc(true_rec, pred_rec):
    """AUC with float label
    """
    rec = [(p, t) for p, t in zip(pred_rec, true_rec)]
    rec = sorted(rec, key=itemgetter(0), reverse=True)

    sum_pospair = 0.0
    sum_npos = 0.0
    sum_nneg = 0.0
    buf_pos = 0.0
    buf_neg = 0.0
    for j in xrange(len(rec)):
        ctr = rec[j][1]
        # keep bucketing predictions in same bucket
        if (j != 0 and rec[j][0] != rec[j - 1][0]):
            sum_pospair += buf_neg * (sum_npos + buf_pos * 0.5)
            sum_npos += buf_pos
            sum_nneg += buf_neg
            buf_neg = 0.0
            buf_pos = 0.0
        buf_pos += ctr
        buf_neg += (1.0 - ctr)
    sum_pospair += buf_neg * (sum_npos + buf_pos * 0.5)
    sum_npos += buf_pos
    sum_nneg += buf_neg
    # this is the AUC
    sum_auc = sum_pospair / (sum_npos*sum_nneg)
    return sum_auc


def libsvm2tfrecord(input_file, output_file):
    writer = tf.python_io.TFRecordWriter(output_file)
    for line in open(input_file, 'r'):
        data = line.split(' ')
        label = float(data[0])
        ids = []
        values = []
        for fea in data[1:]:
            fea_id, value = fea.split(':')
            ids.append(int(fea_id))
            values.append(float(value))

        # Write each example one by one
        example = tf.train.Example(features=tf.train.Features(feature={
            "label":
                tf.train.Feature(float_list=tf.train.FloatList(value=[label])),
            "ids":
                tf.train.Feature(int64_list=tf.train.Int64List(value=ids)),
            "values":
                tf.train.Feature(float_list=tf.train.FloatList(value=values))
        }))
        writer.write(example.SerializeToString())
    writer.close()
    print("Successfully convert {} to {}".format(input_file, output_file))


if __name__ == '__main__':
    bs = BinSpliter()
    data = np.random.rand(30)
    bs.add_bin(data, 't', 5)
    print(bs.data)
    print(bs.find_bin('t', 0.0), bs.find_onehot('t', 0))
    print(bs.find_bin('t', 0.3), bs.find_onehot('t', 0.3))
    print(bs.find_bin('t', 0.7), bs.find_onehot('t', 0.7))
    print(bs.find_bin('t', 1.0), bs.find_onehot('t', 1.))
    bs.save_bin('ttt')
