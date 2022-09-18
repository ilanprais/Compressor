from copyreg import pickle
from typing import List, Tuple
import numpy as np
from functools import lru_cache
import time
import pickle

def compress(text: str) -> bytes:
    return str(generate_compressed_tuples(text)).encode()

def decompress(compressed_text: bytes) -> str:
    tuples = eval(compressed_text.decode())
    return generate_text_from_tuples_recursively(tuples, "")


def generate_text_from_tuples_recursively(tuples: List[Tuple], current_text: str):
    current_text = ""
    current_idx = 0
    while current_idx < len(tuples):
        offset, length, letter = tuples[current_idx]
        current_text = current_text + letter
        if length > offset + 1:
            tuples[current_idx] = offset, length - offset, letter
            current_text += current_text[-offset:-1] 
        else:
            current_idx += 1
        current_text += current_text[-offset:-offset+length-1]
    return current_text


def generate_compressed_tuples(text: str) -> Tuple[int, int, str]:
    locs = []
    i = 0
    while i < len(text):
        from_index, length = longest_match(text, i)
        locs.append((i - from_index ,length, text[i]))
        i += length
    return locs
            

def longest_match(text: str, current_index: int) -> Tuple[int, int]:
    
    lens = np.array([longest_match_from_index(text, i, current_index) for i in range(current_index)])
    from_index = np.argmax(lens) if len(lens) > 0 else None
    length = np.max(lens) if len(lens) > 0 else 0

    if length == 0:
        return current_index, 1

    return from_index, length
    


def longest_match_from_index(text: str, from_index: int, current_index: int) -> int:
    return longest_common_prefix(from_index, current_index, text)


@lru_cache(maxsize=1)
def longest_common_prefix(i: int, j: int, x: str) -> int:
    if 0 <= i < j and 0 <= j < len(x) and x[i] == x[j]:
        return 1 + longest_common_prefix(i + 1, j + 1, x)
    else:
        return 0


txt = open("dickens.txt", "r").read(10000)
# open("dickens_10k.txt", "w").write(txt)
start = time.time()
comp = compress(txt)
print(comp)
open("dickens_compressed_10k.txt", "wb").write(comp)

decomp = decompress(comp)
print(decomp)

open("dickens_decompressed_10k.txt", "w").write(decomp)
