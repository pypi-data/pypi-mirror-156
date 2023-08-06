# word2emoji

This simple module exposes one method to convert a single, english
word to an emoji:

    import word2emoji

    print(word2emoji.lookup("beer"))

    >>> 🍺

It works by way of a simple lookup table. You could use a pretrained
model, but given that there are only a limited set of words in English
it doesn't seem worth it. To build the look up table you need to run
a number of steps:

### Create the training set
The `training.txt` file contains a simple set to train on. 
`test_to_training.py` will convert it to `training_prepared.jsonl` which
can be consumed by openai. Before you can get started, set your OPENAI_KEY:

    export export OPENAI_API_KEY="sk-urshouldgohere"

You can then train fine tune the model. I use davinci:

    openai api fine_tunes.create -t training_prepared.jsonl -m davinci

This will take a few minutes (it does require the )

### Creating the lookup table
Now you are ready to create the lookup. This is done using

    python create_db.py

Update the name of the model there if you want to use your own and
delete/update `words.json` - this contains a dictionary from
word-stem to (word, emoji) pair.

Once you are happy with your new db, you can run:

    python flatten_db.py



