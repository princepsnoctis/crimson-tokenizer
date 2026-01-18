import regex
import json

from .utils import get_counts, merge, escape, decode_bytes, encode_bytes



_DEFAULT_REGEX_PATTERN = r"""
    (
      \p{L}+(?:[’']\p{L}+)*     # words with apostrophe
    | \p{N}{1,3}                # 3-digit numbers
    | -                         # dash
    | [^\r\n\p{L}\p{N}\s]+      # other symbols/punctuation
    | \s*[\r\n]                 # newline
    | \s+(?!\S)                 # line finishing whitespace
    | \s+                       # whitespace
    )
"""



class Tokenizer:
    def __init__(self, regex_pattern=_DEFAULT_REGEX_PATTERN):
        self.merges = {}
        self.vocabulary = {}

        self.regex_pattern = regex_pattern
        self.compiled_regex_pattern = regex.compile(regex_pattern, regex.VERBOSE)

        self.special_tokens = {} # TODO

    def train(self, text, vocabulary_size, verbose=False):
        """
        Given text and a target vocabulary size, it encodes text to bytes,
        finds the most frequent byte pair, merges all such pairs into a
        new index, and repeats until the vocabulary reaches the target size.
        It updates self.merge and self.vocabulary.
        """
        assert vocabulary_size > 255

        parts = regex.findall(self.compiled_regex_pattern, text)
        parts = [part.encode("utf-8") for part in parts]

        self.merges = {}
        self.vocabulary = {idx: bytes([idx]) for idx in range(256)}

        for idx in range(256, vocabulary_size):
            counts = {}

            for part in parts:
                counts = get_counts(part, counts)

            pair = max(counts, key=counts.get)

            if verbose:
                l = escape(self.decode([pair[0]]))
                r = escape(self.decode([pair[1]]))

                print(f"{idx-255:6d} | {l!r:32} + {r!r:32} -> {idx!r}")

            parts = [merge(part, pair, idx) for part in parts]

            self.merges[pair] = idx
            self.vocabulary[idx] = self.vocabulary[pair[0]] + self.vocabulary[pair[1]]

    def _encode_part(self, part):
        while len(part) > 1:
            counts = get_counts(part)

            pair = min(counts, key=lambda x: self.merges.get(x, float("inf")))

            if pair not in self.merges:
                break

            idx = self.merges[pair]

            part = merge(part, pair, idx)

        return part

    def encode(self, text):
        """
        Given text it turns it into a list of bytes and repeatedly applies
        the highest-priority merge learned during training until no merges apply.
        Returns a list of indices.
        """
        parts = regex.findall(self.compiled_regex_pattern, text)
        parts = [part.encode("utf-8") for part in parts]

        idxs = []

        for part in parts:
            part = self._encode_part(part)

            idxs.extend(part)

        return idxs

    def decode(self, idxs):
        """
        Given a list of indices it expands them into bytes and decodes UTF-8.
        Returns the decoded text.
        """
        idxs = b"".join(self.vocabulary[idx] for idx in idxs)

        text = idxs.decode("utf-8", errors="replace")

        return text

    def save(self, path):
        merges = {idx: list(pair) for pair, idx in self.merges.items()}
        vocabulary = {idx: encode_bytes(byte) for idx, byte in self.vocabulary.items()}

        data = {
            "name":           "crimson-tokenizer",
            "version":        "v1",
            "regex_pattern":  self.regex_pattern,
            "special_tokens": self.special_tokens,
            "merges":         merges,
            "vocabulary":     vocabulary,
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def load(self, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        name, version = data.get("name"), data.get("version")

        assert name == "crimson-tokenizer", "The file is not a valid crimson-tokenizer save"

        match version:
            case "v1":
                merges = {tuple(pair): int(idx) for idx, pair in data["merges"].items()}
                vocabulary = {int(idx): decode_bytes(byte) for idx, byte in data["vocabulary"].items()}

                self.regex_pattern =  data["regex_pattern"]
                self.special_tokens = data["special_tokens"]
                self.merges =         merges
                self.vocabulary =     vocabulary

                self.compiled_regex_pattern = regex.compile(self.regex_pattern, regex.VERBOSE)

            case _:
                raise Exception(f"Unsupported save version: {version}")