from operator import itemgetter

class BWT():

    def suffix_array(self, arr):
        arr_size = len(arr)
        arr_int = {v: k for k, v in enumerate(sorted(set(arr)))}
        arr = [arr_int[x] for x in arr]
        arr.append(-1)
        suf = [[i, arr[i], arr[i + 1]] for i in range(arr_size)]
        suf.sort(key=itemgetter(1, 2))
        idx = [0] * arr_size
        k = 2
        while k < arr_size:
            r = 0
            prev_r = suf[0][1]
            for i in range(arr_size):
                if suf[i][1] != prev_r or suf[i - 1][2] != suf[i][2]:
                    r += 1
                prev_r = suf[i][1]
                suf[i][1] = r
                idx[suf[i][0]] = i
            for i in range(arr_size):
                next_idx = suf[i][0] + k
                suf[i][2] = suf[idx[next_idx]][1] if next_idx < arr_size else -1
            suf.sort(key=itemgetter(1, 2))
            k <<= 1
        return [x[0] for x in suf]


    def transform(self, data):
        data_ref = self.suffix_array(data)
        return "".join(data[x-1] for x in data_ref), data_ref.index(0)


    def restore(self, data, idx):
        out = ""
        sorted_data_ref = [i for i, _ in sorted(enumerate(data), key=itemgetter(1))]
        for i in range(len(data)):
            idx = sorted_data_ref[idx]
            out += data[idx]
        return out
