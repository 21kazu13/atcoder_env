class RollingHash():
    def __init__(self,s,base,mod=(1<<61)-1) -> None:
        self.mod = mod
        # A~Z: 65~90, a-z: 97~122
        # base should be grater than 122
        self.base = base
        l = len(s)
        inv = pow(base,-1,mod)
        self.inv = [1]*(l+1)
        self.data = [0]*(l+1)
        self.pows = [1]*(l+1)
        for i in range(l):
            self.inv[i+1] = self.inv[i]*inv%mod
            self.pows[i+1] = self.pows[i]*base%mod
            self.data[i+1] = (self.data[i]+ord(s[i])*self.pows[i])%mod

    def calc(self,l,r):
        # l,r: 0-indexed
        # return hash of [l,r)
        ret = ((self.data[r]-self.data[l])*self.inv[l])%self.mod
        return ret

from random import randint
# base should be random and greater than 122 (=ord('z'))

