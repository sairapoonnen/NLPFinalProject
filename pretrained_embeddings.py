import pickle
import re


def read_embeddings_from_file(file_path, word_whitelist=None):
    embeddings = {}
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            row = line.split()
            word = row[0]
            if word_whitelist is not None and word not in word_whitelist:
                continue

            vector = [float(x) for x in row[1:]]
            embeddings[word] = vector

    return embeddings

