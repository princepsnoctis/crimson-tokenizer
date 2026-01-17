# Given a list of indices returns a count of each pair in that list
def get_counts(idxs):
    counts = {}

    for pair in zip(idxs, idxs[1:]):
        counts[pair] = counts.get(pair, 0) + 1

    return counts



# Given a list of indices, a pair to merge and a new index to replace the pair with, replaces all pairs occurring in that list with given index, from left to right
def merge(idxs, pair, idx):
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



# Given a list of indices and a target vocabulary size it repetitively looks for the most frequently occurring pair and replaces it with a new index. It does so until vocabulary size reaches the targeted quantity. It returns a dictionary of merges
def train(idxs, vocabulary_size):
    merges = {}

    for idx in range(256, vocabulary_size+1):
        counts = get_counts(idxs)

        pair = max(counts, key=counts.get)

        idxs = merge(idxs, pair, idx)

        merges[pair] = idx

    return merges



# Given a dictionary of merges it produces a vocabulary dictionary
def get_vocabulary(merges):
    vocabulary = {idx: bytes([idx]) for idx in range(256)}

    for (p0, p1), idx in merges.items():
        vocabulary[idx] = vocabulary[p0] + vocabulary[p1]

    return vocabulary



# Given a vocabulary dictionary it decodes a list of composite indices into a list of prime indices and concatenates them into a byte object. Then it decodes the byte object into text using UTF-8. It returns the text
def decode(idxs, vocabulary):
    idxs = b"".join(vocabulary[idx] for idx in idxs)

    text = idxs.decode("utf-8", errors="replace")

    return text



# Given text and merges history it turns the text into list of bytes and repetitively looks for a pair that occurred the most frequently during training process, and it merges all such pairs in the list until the text if fully encoded. It returns a list of composite indices
def encode(text, merges):
    idxs = text.encode("utf-8")

    while len(idxs) > 1:
        pair = min(get_counts(idxs), key=lambda x: merges.get(x, float("inf")))

        if pair not in merges:
            break

        idx = merges[pair]

        idxs = merge(idxs, pair, idx)

    return idxs



# TRAINING
training_data = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. In finibus metus vel pulvinar convallis. Aliquam et arcu dictum, imperdiet mi ut, pretium mi. Proin efficitur lorem ac diam viverra, et scelerisque sem porta. Nullam volutpat tincidunt tellus aliquet semper. Proin semper, risus ac posuere cursus, nunc ante sagittis nisl, non facilisis purus diam ut nisl. Maecenas vel justo ut est volutpat sollicitudin. Morbi accumsan tellus eu massa interdum congue. Maecenas ac suscipit risus. Cras dictum risus eu ipsum tincidunt, et molestie enim aliquam. Sed vel consequat risus. Aenean accumsan odio augue, a laoreet orci tempus et.

Vivamus euismod enim in ex finibus posuere. Phasellus odio massa, rutrum in pellentesque eu, consequat eu magna. Sed mollis ac nibh convallis dignissim. Aliquam id rhoncus augue, sed suscipit est. Suspendisse potenti. In massa diam, faucibus id pulvinar interdum, ullamcorper hendrerit risus. Phasellus varius ipsum quis egestas condimentum.

Vestibulum dignissim condimentum condimentum. Mauris ut ante eget ex pretium ornare. Etiam fringilla nisl quis metus dignissim vehicula ac ac massa. Duis ac rhoncus augue. Ut sit amet lorem tortor. Aliquam quis imperdiet massa, eget tristique lorem. Sed egestas ante quam, vel malesuada nunc vulputate a. Curabitur pellentesque iaculis accumsan. In hendrerit tincidunt augue, non vestibulum erat pellentesque in. Nunc rutrum rutrum massa ac sodales. Vestibulum malesuada mattis pulvinar. Ut feugiat non ipsum sed vehicula.

Donec sed tellus vitae sem tempus interdum. Cras a ante dignissim, interdum leo eu, lacinia sapien. Mauris placerat nisl nec pretium aliquam. Mauris pellentesque justo quis blandit rutrum. Curabitur vestibulum nisi mattis hendrerit ultrices. Maecenas maximus dapibus lectus. Sed sit amet tristique purus. Maecenas non lorem porta, laoreet ante non, aliquet orci. Vestibulum volutpat in diam venenatis facilisis. Duis semper massa ex. Integer eget pretium lacus.

Aliquam vitae ex eget sapien pulvinar fringilla at sit amet massa. Duis pharetra sed lectus a efficitur. Etiam in scelerisque mi, quis gravida tortor. Maecenas pellentesque, est eget tincidunt placerat, eros sem bibendum magna, non euismod turpis eros finibus erat. Curabitur pharetra nulla sed tempor malesuada. Duis eget interdum dui, at malesuada neque. Vivamus sit amet orci enim. Cras vitae erat tellus. Integer sed porttitor augue. Nunc et augue non orci ultrices posuere a nec velit. Nam at tincidunt lectus. In diam tortor, sodales et nisl aliquet, mollis malesuada ligula."""

idxs = training_data.encode("utf-8")

merges = train(idxs, 1193)

vocabulary = get_vocabulary(merges)

# INFERENCE
text = "Hello World!";                           print("Original bytes:       ", list(text.encode("utf-8")))

encoded_text = encode(text, merges);             print("Bytes of encoded text:", encoded_text)
decoded_idxs = decode(encoded_text, vocabulary); print("Decoded text:         ", decoded_idxs)