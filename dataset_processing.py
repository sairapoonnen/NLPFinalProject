import html
import pandas
from io import StringIO


def read_twitter_stock_data(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        file_text = f.read()

        file_text = html.unescape(file_text)
        df = pandas.read_csv(StringIO(file_text), sep=";")
        return df[df["sentiment"].notnull()]