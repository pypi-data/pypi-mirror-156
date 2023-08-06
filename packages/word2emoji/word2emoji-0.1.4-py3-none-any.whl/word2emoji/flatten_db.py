import bz2
import json

if __name__ == "__main__":

    db = json.load(open("words.json"))
    stem_db = {}
    with open("flattened.txt", "w") as fout:
        for stem, pl in db.items():
            if pl is not None:
                word, emoji = pl
                fout.write(word + ":" + emoji + "\n")
                stem_db[stem] = emoji

    with bz2.BZ2File("stem_db.jsz2", "w") as fout:
        fout.write(json.dumps(stem_db).encode("utf8"))
