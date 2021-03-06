# encoding=utf-8
import pickle

import numpy as np
from gensim.models import KeyedVectors
from keras.utils import Sequence
from keras.utils import to_categorical

from config import batch_size, vocab_size_zh, Tx, Ty, unknown_word, unknown_embedding, \
    embedding_size, n_s

print('loading fasttext en word embedding')
word_vectors_en = KeyedVectors.load_word2vec_format('data/wiki.en.vec')


class DataGenSequence(Sequence):
    def __init__(self, usage):
        self.usage = usage

        print('loading {} samples'.format(usage))
        if usage == 'train':
            samples_path = 'data/samples_train.p'
        else:
            samples_path = 'data/samples_valid.p'

        samples = pickle.load(open(samples_path, 'rb'))
        self.samples = samples
        np.random.shuffle(self.samples)

    def __len__(self):
        return int(np.ceil(len(self.samples) / float(batch_size)))

    def __getitem__(self, idx):
        i = idx * batch_size

        length = min(batch_size, (len(self.samples) - i))

        batch_x = np.zeros((length, Tx, embedding_size), np.float32)
        batch_y = np.zeros((length, Ty, vocab_size_zh), np.int32)

        s0 = np.zeros((length, n_s))
        c0 = np.zeros((length, n_s))

        for i_batch in range(length):
            sample = self.samples[i + i_batch]

            input_size = min(Tx, len(sample['input']))
            for idx in range(input_size):
                word = sample['input'][idx]
                if word == unknown_word:
                    batch_x[i_batch, idx] = unknown_embedding
                else:
                    batch_x[i_batch, idx] = word_vectors_en[word]

            output_size = min(Ty, len(sample['output']))
            for idx in range(output_size):
                batch_y[i_batch, idx] = to_categorical(sample['output'][idx], vocab_size_zh)

        targets = list(batch_y.swapaxes(0, 1))
        return [batch_x, s0, c0], targets

    def on_epoch_end(self):
        np.random.shuffle(self.samples)


def train_gen():
    return DataGenSequence('train')


def valid_gen():
    return DataGenSequence('valid')
