from bitarray import bitarray
from borrows_wheeler_transform import BWT

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
            L, I = self.bwt.transform(open(file_path, "r").read())
            print("Done transforming!")
            data = L.encode()
            output_buffer.frombytes(I.to_bytes(length=4, byteorder="big")) # L Can be up to 4 bytes in size
        else:
            data = open(file_path, "rb").read()
            
        print("Encoding...")

        i = 0
        seq_char = None
        seq_len = 0
        for c in data:
            if seq_len == 0:
                seq_char = c
                seq_len = 1
            elif c != seq_char or seq_len >= 15: # make sure len fits in 4 bits
                print(seq_char, seq_len)
                output_buffer.frombytes(bytes([seq_char]))
                output_buffer.extend('{0:04b}'.format(seq_len)) # 4 bits
                seq_char = c
                seq_len = 1
            else:
                seq_len += 1

        # print(seq_char, seq_len)
        output_buffer.frombytes(bytes([seq_char]))
        output_buffer.extend('{0:04b}'.format(seq_len)) # 4 bits

        output_buffer.fill()
        
        print("Done Encoding!")

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
            
        print("Decoding...")

        i = 0
        while i <= len(data) - 12:
            output_buffer.append(data[i:i+8].tobytes()*int(data[i+8:i+12].to01(), 2))
            i += 12

        output = b''.join(output_buffer)
        
        print("Done Decoding!")
        
        print("Restoring...")

        if self.bwt:
            output = self.bwt.restore(output.decode(), I).encode()
        
        print("Done Restoring!")

        with open(decompressed_file_path, "wb") as out:
            out.write(output)

        return output

rle = RLE(bwt=BWT())

comp = rle.compress("dickens_500k.txt", "d_c_rl_500k")

decomp = rle.decompress("d_c_rl_500k", "d_c_rl_500k_decomp.txt")
