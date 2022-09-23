from enum import unique
from operator import le
from bitarray import bitarray
from borrows_wheeler_transform import BWT
import numpy as np

class RLE():
    
    '''
    Run-Length Encoding with BWT. 
    Example:
    abababab -> (BWT) -> aaaabbbb -> (RLE) -> a4b4 -> [a][0100][b][0100]
    8 bytes -> 3 bytes
    
    Encoding structure:
    [BWT - L][REP SIZE][c][rep][c][rep][c][rep]...
        4        1      1   d   1   d   1   d    ------> 5 + length(1 + REP_SIZE) bytes
    '''

    def __init__(self, bwt: BWT = None) -> None:
        self.bwt = bwt


    def compress(self, file_path: str, compressed_file_path: str) -> bytes:

        output_buffer = bitarray(endian='big')

        if self.bwt:
            print("Transforming...")
            L = self.bwt.transform(open(file_path, "r").read())
            print("Done transforming!")
            data = L.encode()
        else:
            data = open(file_path, "rb").read()
            
        print("Encoding...")

        sequences = self.extract_sequence_tuples(data)
        len_bound = self.find_optimal_max_seq_length(list(zip(*sequences))[1])
        rep_size = len_bound.bit_length()
        precise_len_bound = 2 ** (rep_size) - 1

        output_buffer.frombytes(rep_size.to_bytes(length=1, byteorder="big")) # rep_size Can be up to 1 byte in size

        for char, len in sequences:
            while len > precise_len_bound:
                output_buffer.frombytes(bytes([char]))
                output_buffer.extend(f'{precise_len_bound:0{rep_size}b}') # rep_size bits
                len -= precise_len_bound

            output_buffer.frombytes(bytes([char]))
            output_buffer.extend(f'{len:0{rep_size}b}') # rep_size bits

        output_buffer.fill()
        
        print("Done Encoding!")

        with open(compressed_file_path, "wb") as out:
            out.write(output_buffer.tobytes())
        
        return output_buffer.tobytes()

    
    def decompress(self, compressed_file_path: str, decompressed_file_path: str) -> bytes:
        data = bitarray(endian='big')
        data.frombytes(open(compressed_file_path, "rb").read())
        output_buffer = []
            
        print("Decoding...")

        rep_size = int.from_bytes(data[0:8], byteorder="big")
        del data[0:8]

        i = 0
        while i <= len(data) - 8 - rep_size:
            output_buffer.append(data[i:i+8].tobytes()*int(data[i+8:i+8+rep_size].to01(), 2))
            i += 8 + rep_size

        output = b''.join(output_buffer)
        
        print("Done Decoding!")

        if self.bwt:
            print("Restoring...")
            output = self.bwt.restore(output.decode()).encode()
            print("Done Restoring!")
        
        with open(decompressed_file_path, "wb") as out:
            out.write(output)

        return output


    def compress_v2(self, file_path: str, compressed_file_path: str) -> bytes:

        output_buffer = bitarray(endian='big')

        if self.bwt:
            print("Transforming...")
            L = self.bwt.transform(open(file_path, "r").read())
            print("Done transforming!")
            data = L.encode()
        else:
            data = open(file_path, "rb").read()
            
        print("Encoding...")

        sequences = self.extract_sequence_tuples(data)

        for char, len in sequences:
            
            len_bit_length = len.bit_length()

            len_bits_size = 3
            max_len_bit_length = 2 ** len_bits_size - 1
            max_len = 2**max_len_bit_length - 1

            while len > max_len:
                output_buffer.frombytes(bytes([char]))
                output_buffer.extend(f'{max_len_bit_length:0{len_bits_size}b}') # 3 bits - maximum len bits = 7 -> maximum len = 127
                output_buffer.extend(f'{max_len:0{max_len_bit_length}b}') # len_bit_length bits
                len -= max_len
                len_bit_length = len.bit_length()


            output_buffer.frombytes(bytes([char]))
            output_buffer.extend(f'{len_bit_length:0{len_bits_size}b}') # 3 bits - maximum len bits = 7 -> maximum len = 127
            output_buffer.extend(f'{len:0{len_bit_length}b}') # len_bit_length bits

        output_buffer.fill()
        
        print("Done Encoding!")

        with open(compressed_file_path, "wb") as out:
            out.write(output_buffer.tobytes())
        
        return output_buffer.tobytes()


    def decompress_v2(self, compressed_file_path: str, decompressed_file_path: str) -> bytes:
        data = bitarray(endian='big')
        data.frombytes(open(compressed_file_path, "rb").read())
        output_buffer = []
            
        print("Decoding...")

        while len(data) > 10:
            rep_bit_length = int(data[8:11].to01(), 2)
            output_buffer.append(data[0:8].tobytes()*int(data[11:11+rep_bit_length].to01(), 2))
            del data[0:11+rep_bit_length]

        output = b''.join(output_buffer)
        
        print("Done Decoding!")

        if self.bwt:
            print("Restoring...")
            output = self.bwt.restore(output.decode()).encode()
            print("Done Restoring!")
        
        with open(decompressed_file_path, "wb") as out:
            out.write(output)

        return output

    
    def find_optimal_max_seq_length(self, lengths):
        return int(
            np.argmin(
                [(l.bit_length() + 8 * np.ceil(np.divide(lengths, l))).sum() for l in range(2, max(lengths))]
            ) + 1     
        )


    def extract_sequence_tuples(self, data: bytes):
        tuples = []
        i = 0
        seq_char = None
        seq_len = 0
        for c in data:
            if seq_len == 0:
                seq_char = c
                seq_len = 1
            elif c != seq_char:
                tuples.append((seq_char, seq_len))
                seq_char = c
                seq_len = 1
            else:
                seq_len += 1

        tuples.append((seq_char, seq_len))

        return tuples


rle = RLE(bwt=BWT())

comp = rle.compress_v2("dickens_100k.txt", "d_c_rl_100k_v2")

decomp = rle.decompress_v2("d_c_rl_100k_v2", "d_c_rl_100k_v2_decomp.txt")
