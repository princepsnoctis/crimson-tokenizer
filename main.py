total_dupes = 0

def step(bytes):
    global total_dupes

    pairs = [(bytes[i], bytes[i+1]) for i in range(len(bytes) - 1)]

    pair_counts = {}

    for pair in pairs:
        pair_counts[pair] = pair_counts.get(pair, 0) + 1

    mac_count = 1
    max_pair = None

    for pair, count in pair_counts.items():
        if count > mac_count:
            mac_count = count

            max_pair = pair

    if max_pair is None: return None

    total_dupes += 1

    new_bytes = []

    i = 0

    while i < len(bytes) - 1:
        bt1 = bytes[i]
        bt2 = bytes[i+1]

        if bt1 == max_pair[0] and bt2 == max_pair[1]:
            # If it's the most frequent pair then substitute new token.
            new_bytes.append(0xFF + total_dupes)

            i += 1
        else:
            # If it's a regular pair then append the first token, pairs are overlapping in the loop so the second element will be covered in next iteration
            new_bytes.append(bt1)

            if i == len(bytes) - 2:
                new_bytes.append(bt2)

        i += 1

    return new_bytes

string = "Hello World! ✅✅✅ 나는 어머니를 먹었다"

bytes = string.encode("utf-8")

new_bytes = bytes

while new_bytes is not None:
    new_bytes = step(new_bytes)

    if new_bytes is not None:
        bytes = new_bytes

print(len(bytes))
