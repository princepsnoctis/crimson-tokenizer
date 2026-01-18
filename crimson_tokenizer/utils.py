import base64



def get_counts(idxs, counts=None):
    """
    Given a list of indices returns a dictionary of counts of each
    consecutive pair in that list
    """

    if counts is None: counts = {}

    for pair in zip(idxs, idxs[1:]):
        counts[pair] = counts.get(pair, 0) + 1

    return counts

def merge(idxs, pair, idx, counts):
    """
    Given a list of indices, a pair to merge and a new index to replace
    the pair with, replaces all consecutive pairs occurring in that
    list with given index, from left to right
    """
    new_idxs = []

    i = 0

    while i < len(idxs):
        if i + 1 < len(idxs) and idxs[i] == pair[0] and idxs[i+1] == pair[1]:
            """
            When merging (a, b, c, d, e, f) -> (a, b, X, e, f)  only 5 pairs are affected:
            (a, b) -> unaffected
            (b, c) -> removed
            (c, d) -> removed
            (d, e) -> removed
            (e, f) -> unaffected
            
            (b, X) -> added
            (X, e) -> added
            """
            prev = new_idxs[-1] if new_idxs else None         # idx before pair
            next = idxs[i + 2] if i + 2 < len(idxs) else None # idx after pair

            _decrease(counts, pair) # Decrease the count for merged pair because it disappears

            if prev is not None:
                _decrease(counts, (prev, pair[0]))
                counts[(prev, idx)]     += 1

            if next is not None:
                _decrease(counts, (pair[1], next))
                counts[(idx, next)]     += 1

            new_idxs.append(idx)
            i += 2
        else:
            new_idxs.append(idxs[i])
            i += 1

    return new_idxs

def escape(string):
    return string.encode("unicode_escape").decode("utf-8")

def encode_bytes(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")

def decode_bytes(s: str) -> bytes:
    return base64.b64decode(s.encode("ascii"))

def _decrease(counts, pair):
    counts[pair] -= 1

    if counts[pair] <= 0:
        del counts[pair]