# encoding=utf-8
import pickle

import keras
import numpy as np
from keras.preprocessing import sequence
from keras.utils import Sequence

from config import batch_size, vocab_size_en, vocab_size_zh, max_token_length_en, max_token_length_zh


class DataGenSequence(Sequence):
    def __init__(self, usage):
        self.usage = usage

        vocab_zh = pickle.load(open('data/vocab_train_zh.p', 'rb'))
        self.idx2word_zh = sorted(vocab_zh)
        self.word2idx_zh = dict(zip(self.idx2word_zh, range(len(vocab_zh))))

        filename = 'data/encoded_{}_images.p'.format(usage)
        self.image_encoding = pickle.load(open(filename, 'rb'))

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
        batch_image_input = np.empty((length, 2048), dtype=np.float32)
        batch_y = np.empty((length, vocab_size_zh), dtype=np.int32)
        text_input = []

        for i_batch in range(length):
            sample = self.samples[i + i_batch]
            image_id = sample['image_id']
            image_input = np.array(self.image_encoding[image_id])
            text_input.append(sample['input'])
            batch_image_input[i_batch] = image_input
            batch_y[i_batch] = keras.utils.to_categorical(sample['output'], vocab_size_zh)

        batch_text_input = sequence.pad_sequences(text_input, maxlen=max_token_length_en, padding='post')
        return [batch_image_input, batch_text_input], batch_y

    def on_epoch_end(self):
        np.random.shuffle(self.samples)


def train_gen():
    return DataGenSequence('train')


def valid_gen():
    return DataGenSequence('valid')
