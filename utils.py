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



def escape(string):
    return string.encode("unicode_escape").decode("utf-8")