import json
import os
import openai
from nltk.stem.porter import PorterStemmer

FINE_TUNED_MODEL = "davinci:ft-personal-2022-06-24-18-48-09"
USE_MODEL = True

if __name__ == "__main__":
    if os.path.isfile("words.json"):
        db = json.load(open("words.json"))
    else:
        db = {}

    if USE_MODEL:
        base_prompt = ""
    else:
        training = open("training.txt").read().splitlines()
        base_prompt = "\n".join(training[:16]) + "\n"

    stemmer = PorterStemmer()
    dirty = False

    for idx, word in enumerate(open("wiki-100k.txt").read().splitlines()[:30000]):
        if idx % 250 == 0 and dirty:
            print(idx)
            dirty = False
            with open("words.json", "w") as fout:
                json.dump(db, fout, indent=2)
        if any(ch < "a" or ch > "z" for ch in word):
            continue
        stem = str(stemmer.stem(word))
        if stem in db:
            continue
        if USE_MODEL:
            prompt = word + ":"
        else:
            prompt = base_prompt + word + ":"
        dirty = True
        completion = openai.Completion.create(
            model=FINE_TUNED_MODEL if USE_MODEL else "text-davinci-002",
            prompt=prompt,
            max_tokens=4,
        )
        emoji = [ch for ch in completion.choices[0].text if ord(ch) > 256]
        if emoji:
            db[stem] = (str(word), str(emoji[0]))
        else:
            db[stem] = None

    with open("words.json", "w") as fout:
        json.dump(db, fout, indent=2)
