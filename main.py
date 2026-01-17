from trainer import train, get_vocabulary, encode, decode


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