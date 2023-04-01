import os
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

chat_language = os.getenv("INIT_LANGUAGE", default="zh")

MSG_LIST_LIMIT = int(os.getenv("MSG_LIST_LIMIT", default=20))
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", default=1000))

LANGUAGE_TABLE = {
    "zh": "嗨！",
    "en": "Hi!"
}

stemmer = PorterStemmer()

def get_similarity_score(s1, s2):
    # tokenize and stem the words in the sentences
    words1 = [stemmer.stem(w.lower()) for w in word_tokenize(s1)]
    words2 = [stemmer.stem(w.lower()) for w in word_tokenize(s2)]

    # compute the Jaccard similarity score
    intersection = set(words1).intersection(set(words2))
    union = set(words1).union(set(words2))
    score = len(intersection) / len(union)
    
    return score

class Prompt:
    def __init__(self):
        self.msg_list = []
        self.load_memory()

    def add_msg(self, new_msg):
        if len(self.msg_list) >= MSG_LIST_LIMIT:
            self.remove_msg()
        self.msg_list.append(new_msg)
        self.save_memory()

    def remove_msg(self):
        self.msg_list.pop(0)

    def generate_prompt(self):
        return '\n'.join(self.msg_list)

    def load_memory(self):
        if not os.path.exists("memory.txt"):
            return
        with open("memory.txt", "r") as f:
            self.msg_list = [line.strip() for line in f.readlines()]
            self.msg_list = self.msg_list[-MEMORY_LIMIT:]

    def save_memory(self):
        with open("memory.txt", "w") as f:
            f.write('\n'.join(self.msg_list[-MEMORY_LIMIT:]))