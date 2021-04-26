import torch
from torch.utils.data import Dataset
from dataset_processing import read_twitter_stock_data, TextFeaturizer
import torch.nn as nn
import pickle


def load_all_data(train_file="train.csv", val_file="val.csv", test_file="test.csv", embedding_file="embeddings_limited.pkl"):
    train_df = read_twitter_stock_data(train_file)
    val_df = read_twitter_stock_data(val_file)
    test_df = read_twitter_stock_data(test_file)

    with open(embedding_file, "rb") as f:
        embeddings = pickle.load(f)
    featurizer = TextFeaturizer(train_df["text"].tolist(), embeddings)

    train_dataset = StockSentimentDataset(train_df, featurizer)
    val_dataset = StockSentimentDataset(val_df, featurizer)
    test_dataset = StockSentimentDataset(test_df, featurizer)

    return train_dataset, val_dataset, test_dataset, embeddings, featurizer


class StockSentimentDataset(Dataset):
    def __init__(self, stock_df, featurizer):
        self.samples = featurizer.featurize(stock_df["text"].tolist())
        self.sentiment_id_mapping = {"negative": 0, "neutral": 1, "positive": 2}
        self.labels = [self.sentiment_id_mapping[s] for s in stock_df["sentiment"].tolist()]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        return {"sample": self.samples[idx], "label": self.labels[idx]}


def collate_fn(data):
    src_ids = [torch.LongTensor(e["sample"]) for e in data]
    labels = [e["label"] for e in data]
    labels_tensor = torch.LongTensor(labels)

    src_seqs = nn.utils.rnn.pad_sequence(src_ids, batch_first=False, padding_value=TextFeaturizer.PADDING_ID)

    return src_seqs, labels_tensor
