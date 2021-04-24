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


def add_special_tokens_to_text(text):
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
