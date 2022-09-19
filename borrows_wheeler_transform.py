import argparse
from operator import itemgetter

class BWT():

    def transform(self, txt: str):
        n = len(txt)
        m = sorted([txt[i:n]+txt[0:i] for i in range(n)])
        I = m.index(txt)
        L = ''.join([q[-1] for q in m])
        return (I, L)

    def restore(self, I, L):
        n = len(L)
        X = sorted([(i, x) for i, x in enumerate(L)], key=itemgetter(1))

        T = [None for i in range(n)]
        for i, y in enumerate(X):
            j, _ = y
            T[j] = i

        Tx = [I]
        for i in range(1, n):
            Tx.append(T[Tx[i-1]])

        S = [L[i] for i in Tx]
        S.reverse()
        return ''.join(S)
