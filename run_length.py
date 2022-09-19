from bitarray import bitarray
from borrows_wheeler_transform import BWT

class RLE():

    def __init__(self, bwt: BWT = None) -> None:
        self.bwt = bwt

    def compress(self, file_path: str, compressed_file_path: str) -> bytes:

        output_buffer = bitarray(endian='big')

        if self.bwt:
            I, L = self.bwt.transform(open(file_path, "r").read())
            data = L.encode()
            output_buffer.frombytes(I.to_bytes(length=4, byteorder="big")) # L Can be up to 4 bytes in size
        else:
            data = open(file_path, "rb").read()

        i = 0
        seq_char = None
        seq_len = 0
        for c in data:
            if seq_len == 0:
                seq_char = c
                seq_len = 1
            elif c != seq_char or seq_len >= 255: # make sure len fits in 8 bits
                print(seq_char, seq_len)
                output_buffer.frombytes(bytes([seq_char]))
                output_buffer.frombytes(bytes([seq_len]))
                seq_char = c
                seq_len = 1
            else:
                seq_len += 1

        # print(seq_char, seq_len)
        output_buffer.frombytes(bytes([seq_char]))
        output_buffer.frombytes(bytes([seq_len]))

        output_buffer.fill()

        with open(compressed_file_path, "wb") as out:
            out.write(output_buffer.tobytes())
        
        return output_buffer.tobytes()


    def decompress(self, compressed_file_path: str, decompressed_file_path: str) -> bytes:
        data = bitarray(endian='big')
        data.frombytes(open(compressed_file_path, "rb").read())
        output_buffer = []

        if self.bwt:
            I = int.from_bytes(data[0:32], byteorder="big")
            del data[0:32]

        i = 0
        while i <= len(data) - 16:
            output_buffer.append(data[i:i+8].tobytes()*ord(data[i+8:i+16].tobytes()))
            i += 16

        output = b''.join(output_buffer)

        if self.bwt:
            output = self.bwt.restore(I, output.decode()).encode()

        with open(decompressed_file_path, "wb") as out:
            out.write(output)

        return output

rle = RLE(bwt=BWT())

comp = rle.compress("dickens_200k.txt", "d_c_rl_200k")

decomp = rle.decompress("d_c_rl_200k", "d_c_rl_200k_decomp.txt")