from copyreg import pickle
from re import T
from typing import List, Tuple
import numpy as np
from functools import lru_cache
import time
from tqdm import tqdm
from bitarray import bitarray

MAX_WINDOW_SIZE = 4000 # 12 bits 
MAX_FORWARD_SIZE = 15 # 4 bits

class LZ77:

    def __init__(self, window_size = 500, forward_size = 15) -> None:
        assert window_size <= MAX_WINDOW_SIZE
        assert forward_size <= MAX_FORWARD_SIZE
        self.window_size = window_size
        self.forward_size = forward_size

    def compress(self, file_path: str, compressed_file_path: str) -> bytes:
        data = open(file_path, "rb")

        output_buffer = bitarray(endian='big')

        i = 0
        with tqdm(total=len(data)) as p:
            while i < len(data):
                from_index, length = self._longest_match(data, i)

                offset = i - from_index
                letter = data[i]

                # print(f"({offset}, {length}, {chr(letter)})")

                if offset > 0:
                    output_buffer.append(True)
                    output_buffer.frombytes(bytes([offset >> 4]))
                    output_buffer.frombytes(bytes([((offset & 0xf) << 4) | length]))
                else:
                    output_buffer.append(False)
                    output_buffer.frombytes(bytes([letter]))

                i += length
                p.update(length)
            
        output_buffer.fill()

        with open(compressed_file_path, "wb") as out:
            out.write(output_buffer.tobytes())
        
        return output_buffer.tobytes()
            

    def decompress(self, compressed_file_path: str, decompressed_file_path: str) -> bytes:

        data = bitarray(endian='big')
        data.frombytes(open(compressed_file_path, "rb").read())
        output_buffer = []

        with tqdm(total=len(data)) as p:
            while len(data) > 0:
                is_pointer = data.pop(0)

                if is_pointer:
                    byte1 = ord(data[0:8].tobytes())
                    byte2 = ord(data[8:16].tobytes())

                    del data[0:16]
                    offset = (byte1 << 4) | (byte2 >> 4)
                    length = (byte2 & 0xf)

                    for i in range(length):
                        output_buffer.append(output_buffer[-offset])

                    p.update(length*8)

                else:
                    output_buffer.append(data[0:8].tobytes())
                    del data[0:8]
                    p.update(8)

        output = b''.join(output_buffer[:-1])

        with open(decompressed_file_path, "wb") as out:
            out.write(output)

        return output
            

    def _longest_match(self, text: str, current_index: int) -> Tuple[int, int]:
        
        lens = np.array([self._longest_match_from_index(text, i, current_index) for i in range(max(0, current_index - self.window_size), current_index)])
        from_index = np.argmax(lens) + max(0, current_index - self.window_size) if len(lens) > 0 else None
        length = np.max(lens) if len(lens) > 0 else 0

        if length == 0:
            return current_index, 1

        return from_index, length


    def _longest_match_from_index(self, text: str, from_index: int, current_index: int) -> int:
        return min(LZ77.longest_common_prefix(from_index, current_index, text), self.forward_size)


    @staticmethod
    @lru_cache(maxsize=1)
    def longest_common_prefix(i: int, j: int, x: str) -> int:
        if 0 <= i < j and 0 <= j < len(x) and x[i] == x[j]:
            return 1 + LZ77.longest_common_prefix(i + 1, j + 1, x)
        else:
            return 0


lz77 = LZ77(window_size=MAX_WINDOW_SIZE)

comp = lz77.compress("dickens_100k.txt", "dickens_compressed_100k")

decomp = lz77.decompress("dickens_compressed_100k", "dickens_decompressed_100k.txt")
