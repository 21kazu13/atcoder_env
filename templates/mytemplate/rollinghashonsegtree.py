from atcoder import segtree
class RollingHashOnSegtree():
    def __init__(self,s,base,mod=(1<<61)-1) -> None:
        self.mod = mod
        # A~Z: 65~90, a-z: 97~122
        # base should be grater than 122
        self.base = base
        l = len(s)
        inv = pow(base,-1,self.mod)
        self.inv = [1]*(l+1)
        self.pows = [1]*(l+1)
        for i in range(l):
            self.inv[i+1] = self.inv[i]*inv%mod
            self.pows[i+1] = self.pows[i]*base%mod
        self.data = segtree.SegTree(
            op=self._op,
            e=0,
            v=[ord(c)*self.pows[idx]%mod for idx,c in enumerate(s)]
        )
    def _op(self,x,y):
        return (x+y)%self.mod
    def prod(self,l,r):
        # l,r: 0-indexed
        # return hash of [l,r)
        return self.data.prod(l,r)*self.inv[l]%self.mod
    def update(self,idx,value):
        v = ord(value)*self.pows[idx]%self.mod
        self.data.set(idx,v)

from random import randint
# base should be random and greater than 122 (=ord('z'))
