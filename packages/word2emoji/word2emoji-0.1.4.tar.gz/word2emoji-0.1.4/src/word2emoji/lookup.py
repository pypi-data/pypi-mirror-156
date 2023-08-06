import bz2
import json
import argparse
import os

from nltk.stem.porter import PorterStemmer

_WORDS = {}
_STEMMER = None

PATH = os.path.join(os.path.dirname(__file__), "stem_db.jsz2")


def look_up(word: str) -> str:
    global _WORDS, _STEMMER
    if not _WORDS:
        with bz2.BZ2File(PATH) as fin:
            _WORDS = json.loads(fin.read())
        _STEMMER = PorterStemmer()
    word = _STEMMER.stem(word)
    return _WORDS.get(word, "💩")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a word to an emoji")
    parser.add_argument(
        "word",
        type=str,
        help="The word to look up",
    )
    args = parser.parse_args()

    print(look_up(args.word))
