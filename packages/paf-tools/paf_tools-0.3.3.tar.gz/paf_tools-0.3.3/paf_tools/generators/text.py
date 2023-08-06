from random import random


def lorem_impsum(word_count: int = 1) -> str:
    words = ["Lorem", "ipsum", "dolor", "sit", "amet", "", "consectetur", "adipisici", "elit", "", "sed", "eiusmod",
             "tempor", "incidunt", "ut", "labore", "et", "dolore", "magna", "aliqua", "", "Ut", "enim", "ad", "minim",
             "veniam", "", "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut", "aliquid", "ex", "ea",
             "commodi", "consequat", "", "Quis", "aute", "iure", "reprehenderit", "in", "voluptate", "velit", "esse",
             "cillum", "dolore", "eu", "fugiat", "nulla", "pariatur", "Excepteur", "sint", "obcaecat", "cupiditat",
             "non", "proident", "", "sunt", "in", "culpa", "qui", "officia", "deserunt", "mollit", "anim", "id", "est",
             "laborum"]
    if word_count == 1:
        return words[random.randint(0, len(words) - 1)]

    return ''.join(f' {words[random.randint(0, len(words) - 1)]}' for _ in range(word_count))