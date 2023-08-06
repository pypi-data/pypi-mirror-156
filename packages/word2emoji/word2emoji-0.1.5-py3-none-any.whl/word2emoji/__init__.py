from .lookup import look_up
import sys

VERSION = "0.1.5"


class Word2Emoji:
    def __call__(self, word: str) -> str:
        return look_up(word)


__all__ = [look_up]
sys.modules[__name__] = Word2Emoji()