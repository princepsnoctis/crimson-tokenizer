from Tokenizer import Tokenizer

tokenizer = Tokenizer()

text = open("lorem_ipsum.txt").read()

tokenizer.train(text, 256 + 500, verbose=True)