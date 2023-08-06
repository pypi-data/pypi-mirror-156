import json

if __name__ == "__main__":
    lines = open("training.txt").read().splitlines()

    with open("training_prepared.jsonl", "w") as fout:
        for line in lines:
            prompt, emoji = line.split(":")
            fout.write(
                json.dumps({"prompt": prompt + ":", "completion": emoji + "\n"}) + "\n"
            )
