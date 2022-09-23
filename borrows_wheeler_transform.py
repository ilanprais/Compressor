from operator import itemgetter

class BWT():

    def transform(self, data):
        n = len(data)
        m = sorted([data[i:n]+data[0:i] for i in range(n)])
        I = m.index(data)
        L = ''.join([q[-1] for q in m])
        return L, I

    def restore(self, data, idx):
        n = len(data)
        X = sorted([(i, x) for i, x in enumerate(data)], key=itemgetter(1))

        T = [None for i in range(n)]
        for i, y in enumerate(X):
            j, _ = y
            T[j] = i

        Tx = [idx]
        for i in range(1, n):
            Tx.append(T[Tx[i-1]])

        S = [data[i] for i in Tx]
        S.reverse()
        return ''.join(S)
