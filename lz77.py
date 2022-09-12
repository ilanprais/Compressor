from typing import Tuple
import numpy as np

def compress(text: str) -> Tuple[int, int, str]:
    locs = [(0, 1, text[0])]
    for i in range(len(text)):
        index, length = longest_match(text, text[i + 1:])
        locs.append((i - index + 1, length, text[i + 1]))
        i += length
    return locs
            

def longest_match(text, current):
    lens = np.array([longest_match_from_index(text, i, current) for i in range(len(text) - len(current))])
    index = np.argmax(lens)
    length = np.max(lens)
    return index, length
    

def longest_match_from_index(text, index, current):
    length = 0
    for j in range(len(current)):
            if text[index + j] == current[j]:
                length += 1
            else:
                break
    return length

txt = open("dickens.txt", "r").read(40)
comp = compress(txt)

print(comp)
