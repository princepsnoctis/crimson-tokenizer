from utils import get_counts, merge, escape



class Tokenizer:
    def __init__(self):
        self.merges = {}
        self.vocabulary = {}

    def train(self, text, vocabulary_size, verbose=False):
        """
        Given text and a target vocabulary size, it encodes text to bytes,
        finds the most frequent byte pair, merges all such pairs into a
        new index, and repeats until the vocabulary reaches the target size.
        It updates self.merge and self.vocabulary.
        """
        idxs = text.encode("utf-8")

        self.merges = {}
        self.vocabulary = {idx: bytes([idx]) for idx in range(256)}

        for idx in range(256, vocabulary_size):
            counts = get_counts(idxs)

            pair = max(counts, key=counts.get)

            if verbose:
                l = escape(self.decode([pair[0]]))
                r = escape(self.decode([pair[1]]))

                print(f"{idx-255:6d} | {l!r:32} + {r!r:32} -> {idx!r}")

            idxs = merge(idxs, pair, idx)

            self.merges[pair] = idx
            self.vocabulary[idx] = self.vocabulary[pair[0]] + self.vocabulary[pair[1]]

    def encode(self, text):
        """
        Given text it turns it into a list of bytes and repeatedly applies
        the highest-priority merge learned during training until no merges apply.
        Returns a list of indices.
        """
        idxs = text.encode("utf-8")

        while len(idxs) > 1:
            pair = min(get_counts(idxs), key=lambda x: self.merges.get(x, float("inf")))

            if pair not in self.merges:
                break

            idx = self.merges[pair]

            idxs = merge(idxs, pair, idx)

        return idxs

    def decode(self, idxs):
        """
        Given a list of indices it expands them into bytes and decodes UTF-8.
        Returns the decoded text.
        """
        idxs = b"".join(self.vocabulary[idx] for idx in idxs)

        text = idxs.decode("utf-8", errors="replace")

        return text
