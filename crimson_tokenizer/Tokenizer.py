from collections import Counter, defaultdict
import heapq

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
        self.compiled_regex_pattern = regex.compile(self.regex_pattern, regex.VERBOSE)

        self.special_tokens = {} # TODO

    def train(self, text, vocabulary_size, verbose=False):
        """
        Trains the tokenizer on provided text until it reaches target vocabulary size.
        """
        assert vocabulary_size > 255

        # Chunk text according to regex
        chunks = regex.findall(self.compiled_regex_pattern, text)
        chunks = [chunk.encode("utf-8") for chunk in chunks]

        # Fill nodes and heads
        nodes = []
        heads = []

        def _add_chunk(chunk):
            head = None
            prev = None

            for token in chunk:
                node_idx = len(nodes)

                nodes.append([token, prev, None])

                if prev is not None:
                    nodes[prev][2] = node_idx

                if head is None:
                    head = node_idx

                prev = node_idx

            if head is not None:
                heads.append(head)

        for chunk in chunks:
            _add_chunk(chunk)

        # Fill pairs
        pairs = defaultdict(set)

        for head in heads:
            this = head

            while nodes[this][2] is not None:
                next = nodes[this][2]

                pair = (nodes[this][0], nodes[next][0])

                pairs[pair].add(this)

                this = next

        # Create heap for efficient most frequent pair picking
        heap = [(-len(positions), pair) for pair, positions in pairs.items()]
        heapq.heapify(heap)

        # Merge repeatedly
        self.merges = {}
        self.vocabulary = {idx: bytes([idx]) for idx in range(256)}

        for idx in range(256, vocabulary_size):
            # Pick the most frequent pair
            while heap:
                negative_count, pair = heapq.heappop(heap)

                if pair not in pairs or -negative_count != len(pairs[pair]):
                    continue # stale entry

                break
            else:
                break # no pairs left

            positions = list(pairs[pair])
            pairs[pair].clear()

            for position in positions:
                """
                Situation:
                ..., a, b, prev, this, that, next, y, z, ...
                """
                this = position
                that = nodes[position][2]

                if that is None:
                    continue

                if (nodes[this][0], nodes[that][0]) != pair:
                    continue

                prev = nodes[this][1]
                next = nodes[that][2]

                nodes[this][0] = idx  # create merged node
                nodes[this][2] = next # remove that node

                if next is not None:
                    nodes[next][1] = this

                if prev is not None:
                    old = (nodes[prev][0], pair[0])
                    pairs[old].discard(prev)

                    new = (nodes[prev][0], idx)
                    pairs[new].add(prev)

                    heapq.heappush(heap, (-len(pairs[new]), new))

                if next is not None:
                    old = (pair[1], nodes[next][0])
                    pairs[old].discard(that)

                    new = (idx, nodes[next][0])
                    pairs[new].add(next)

                    heapq.heappush(heap, (-len(pairs[new]), new))

            if verbose:
                l = escape(self.decode([pair[0]]))
                r = escape(self.decode([pair[1]]))

                print(f"{idx - 255:6d} | {l!r:32} + {r!r:32} -> {idx!r}")

            self.merges[pair] = idx
            self.vocabulary[idx] = self.vocabulary[pair[0]] + self.vocabulary[pair[1]]

    def _encode_chunk(self, chunk):
        counts = Counter()

        counts.update(zip(chunk, chunk[1:]))

        while len(chunk) > 1:
            pair = min(counts, key=lambda x: self.merges.get(x, float("inf")))

            if pair not in self.merges:
                break

            token = self.merges[pair]

            chunk = merge(chunk, pair, token, counts)

        return chunk

    def encode(self, text):
        """
        Encodes the text into tokens
        """
        chunks = regex.findall(self.compiled_regex_pattern, text)
        chunks = [chunk.encode("utf-8") for chunk in chunks]

        tokens = []

        for chunk in chunks:
            chunk = self._encode_chunk(chunk)

            tokens.extend(chunk)

        return tokens

    def decode(self, tokens):
        """
        Decodes the tokens into text
        """
        tokens = b"".join(self.vocabulary[token] for token in tokens)

        text = tokens.decode("utf-8", errors="replace")

        return text

    def save(self, path):
        merges = {token: list(pair) for pair, token in self.merges.items()}
        vocabulary = {token: encode_bytes(byte) for token, byte in self.vocabulary.items()}

        data = {
            "name":           "crimson-tokenizer",
            "version":        "v1",
            "regex_pattern":  self.regex_pattern,
            "special_tokens": self.special_tokens,
            "merges":         merges,
            "vocabulary":     vocabulary,
        }

        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def load(self, path):
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        name, version = data.get("name"), data.get("version")

        assert name == "crimson-tokenizer", "The file is not a valid crimson-tokenizer save"

        match version:
            case "v1":
                merges = {tuple(pair): int(token) for token, pair in data["merges"].items()}
                vocabulary = {int(token): decode_bytes(byte) for token, byte in data["vocabulary"].items()}

                self.regex_pattern =  data["regex_pattern"]
                self.special_tokens = data["special_tokens"]
                self.merges =         merges
                self.vocabulary =     vocabulary

                self.compiled_regex_pattern = regex.compile(self.regex_pattern, regex.VERBOSE)

            case _:
                raise Exception(f"Unsupported save version: {version}")