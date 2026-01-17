def get_counts(idxs):
    """
    Given a list of indices returns a dictionary of counts of each
    consecutive pair in that list
    """
    counts = {}

    for pair in zip(idxs, idxs[1:]):
        counts[pair] = counts.get(pair, 0) + 1

    return counts



def merge(idxs, pair, idx):
    """
    Given a list of indices, a pair to merge and a new index to replace
    the pair with, replaces all consecutive pairs occurring in that
    list with given index, from left to right
    """
    new_idxs = []

    i = 0

    while i < len(idxs):
        if i + 1 < len(idxs) and idxs[i] == pair[0] and idxs[i+1] == pair[1]:
            new_idxs.append(idx)
            i += 2
        else:
            new_idxs.append(idxs[i])
            i += 1

    return new_idxs



def train(idxs, vocabulary_size):
    """
    Given a list of indices and a target vocabulary size it repetitively
    looks for the most frequently occurring pair and replaces it with a
    new index. It does so until vocabulary size reaches the targeted
    quantity. It returns a dictionary of merges
    """
    merges = {}

    for idx in range(256, vocabulary_size+1):
        counts = get_counts(idxs)

        pair = max(counts, key=counts.get)

        idxs = merge(idxs, pair, idx)

        merges[pair] = idx

    return merges



def get_vocabulary(merges):
    """
    Given a dictionary of merges it produces a vocabulary dictionary and
    returns it
    """

    vocabulary = {idx: bytes([idx]) for idx in range(256)}

    for (p0, p1), idx in merges.items():
        vocabulary[idx] = vocabulary[p0] + vocabulary[p1]

    return vocabulary



def decode(idxs, vocabulary):
    """
    Given a vocabulary dictionary it decodes a list of composite indices
    into a list of prime indices and concatenates them into a byte
    object.Then it decodes the byte object into text using UTF-8.
    It returns the text
    """
    idxs = b"".join(vocabulary[idx] for idx in idxs)

    text = idxs.decode("utf-8", errors="replace")

    return text



def encode(text, merges):
    """
    Given text and merges history it turns the text into list of bytes
    and repetitively looks for a pair that occurred the most
    frequently during training process, and it merges all such pairs
    in the list until the text if fully encoded. It returns a list
    of composite indices
    """
    idxs = text.encode("utf-8")

    while len(idxs) > 1:
        pair = min(get_counts(idxs), key=lambda x: merges.get(x, float("inf")))

        if pair not in merges:
            break

        idx = merges[pair]

        idxs = merge(idxs, pair, idx)

    return idxs