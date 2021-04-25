import html
import pandas
from io import StringIO
import re
from emoji import EMOJI_UNICODE_ENGLISH
import unicodedata


def read_twitter_stock_data(file_path, remove_unlabelled_rows=True):
    with open(file_path, "r", encoding="utf-8") as f:
        file_text = f.read()

        file_text = html.unescape(file_text)
        df = pandas.read_csv(StringIO(file_text), sep=";")

        if remove_unlabelled_rows:
            return df[df["sentiment"].notnull()]
        else:
            return df


class Tokenizer():
    def __init__(self):
        self.word_char_regex = re.compile(r'\w')
        self.whitespace_regex = re.compile(r'\s')
        self.punct_chars = ".!?"
        self.special_tokens = ["<URL>", "<USER>", "<SMILE>", "<LOLFACE>", "<SADFACE>", "<NEUTRALFACE>", "<HEART>",
                          "<NUMBER>"]
        self.emojis = EMOJI_UNICODE_ENGLISH.keys()
        self.max_emoji_len = max([len(e) for e in self.emojis])

    def tokenize(self, text):
        text = self.preprocess_text(text)
        current_token = ""
        tokens = []

        i = 0
        while i < len(text):
            c = text[i]

            if self.word_char_regex.fullmatch(c):
                current_token += c
            else:
                if len(current_token) > 0:
                    if text[i+1:i+8] == "<ELONG>":
                        tokens.append(current_token + " <ELONG>")
                        i += 8
                        current_token = ""
                        continue
                    else:
                        if current_token != "rt":
                            tokens.append(current_token)
                        current_token = ""
                if c in self.punct_chars:
                    if len(current_token) > 0:
                        tokens.append(current_token)
                        current_token = ""
                    if text[i+2:i+10] == "<REPEAT>":
                        tokens.append(c + " <REPEAT>")
                        i += 10
                        continue
                    else:
                        tokens.append(c)
                if c == "<":
                    is_special_token = False
                    for st in self.special_tokens:
                        if text[i:i+len(st)] == st:
                            tokens.append(st)
                            i += len(st)
                            is_special_token = True
                            break
                    if not is_special_token:
                        tokens.append(c)
                    else:
                        continue
                if c in self.emojis:
                    for emote_len in range(self.max_emoji_len, 0, -1):
                        if text[i:i+emote_len] in self.emojis:
                            tokens.append(text[i:i+emote_len])
                            i += emote_len
                            break
                    continue
                if c == "#":
                    tokens.append(c)
                if unicodedata.category(c) == 'So':
                    tokens.append(c)
            i += 1
        if len(current_token) > 0:
            tokens.append(current_token)
        return tokens

    def preprocess_text(self, text):
        text = text.lower()

        url_regex = r'https?://\S+\b|www\.(\w+\.)+\S*'
        user_regex = r'@\w+'
        eyes = "[8:=;]"
        nose = "['`-]?"
        smiley_regex = "({0}{1}[)d]+|[)d]+{1}{0})".format(eyes, nose)
        lol_face_regex = eyes + nose + "p+"
        sad_face_regex = "({0}{1}\\(+|{1}{0}\\))".format(eyes, nose)
        neutral_face_regex = "{0}{1}[\\/|l*]".format(eyes, nose)
        number_regex = r'[-+]?[.\d]*[\d]+[:,.\d]*'
        punct_repitition_regex = r'([!?.]){2,}'
        word_ending_repitition_regex = r'\b(\S*?)(.)\2{2,}\b'

        text = re.sub(r'\s{2,}', ' ', text)
        text = re.sub(r'\'', '', text)
        text = re.sub(url_regex, "<URL>", text)
        text = re.sub(user_regex, "<USER>", text)
        text = re.sub(smiley_regex, "<SMILE>", text)
        text = re.sub(lol_face_regex, "<LOLFACE>", text)
        text = re.sub(sad_face_regex, "<SADFACE>", text)
        text = re.sub(neutral_face_regex, "<NEUTRALFACE>", text)
        text = re.sub("<3", "<HEART>", text)
        text = re.sub(number_regex, "<NUMBER>", text)
        text = re.sub(punct_repitition_regex, lambda match: match.group(1) + " <REPEAT>", text)
        text = re.sub(word_ending_repitition_regex, lambda match: match.group(1) + match.group(2) + " <ELONG>", text)

        return text
