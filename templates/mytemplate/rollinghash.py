class RollingHash():
    '''Calculate and connect Rolling Hash defined by sum(s[i]*base^i)

    Parameters
    ----------
    s : list[int]
        value for hashing.
        All elements should be greater than 0.
    base : int
        Base for hash. 
        Make sure to select between max(s)+1 and mod-1.

    Attributes
    ----------
    mod : int
        Modulo for hash.
        Default is 2^61-1.
    pows : list[int]
        pre-calculated value for base^i
    inv : list[int]
        pre-calculated value for inverse for base^i
    data : list[int]
        hash value for s[0:i]
    
    Methods
    -------
    calc(l,r)
        calculate hash for s[l:r]
    connect(h1,l1,h2)
        calculate hash for concate of h1+h2
    merge(l1,r1,l2,r2)
        calculate hash for [l1,r1)+[l2,r2)
    '''
    # https://ei1333.github.io/luzhiled/snippets/string/rolling-hash.html
    # https://maspypy.com/rolling-hash%E3%81%AB%E3%81%A4%E3%81%84%E3%81%A6%EF%BC%88survey-%E7%A0%94%E7%A9%B6%EF%BC%89
    # https://qiita.com/keymoon/items/11fac5627672a6d6a9f6
    # https://www.slideshare.net/nagisaeto/rolling-hash-149990902
    # https://tjkendev.github.io/procon-library/python/string/rolling_hash.html
    def __init__(self, s: list[int], base: int, mod=(1<<61)-1) -> None:
        self.mod = mod
        assert max(s)<base<mod
        self.base = base
        l = len(s)
        inv = pow(base,-1,mod)
        self.inv = [1]*(l+1)
        self.data = [0]*(l+1)
        self.pows = [1]*(l+1)
        for i in range(l):
            self.inv[i+1] = self.inv[i]*inv%mod
            self.pows[i+1] = self.pows[i]*base%mod
            self.data[i+1] = (self.data[i]+s[i]*self.pows[i])%mod
    
    def calc(self, l: int, r: int) -> int:
        '''Calculate hash for [l:r) with O(1)

        Parameters
        ----------
        l : int
            left index for target section
        r : int
            right index for target section
        
        Returns
        -------
        ret : int
            hashed value for [l:r)
        '''
        ret = ((self.data[r]-self.data[l])*self.inv[l])%self.mod
        return ret

    def connect(self, h1: int, len_l1: int, h2: int) -> int:
        '''Calculate hash for s1+s2 with O(1)

        Parameters
        ----------
        l1 : int
            hashed value for s1
        r1 : int
            length for s1
        h2 : int
            hashed value for s2
        
        Returns
        -------
        ret : int
            hashed value for s1+s2
        '''
        # return hash for h1+h2
        return (h1+h2*self.pows[len_l1])%self.mod

    def merge(self, l1: int, r1: int, l2: int, r2: int) -> int:
        '''Calculate hash for [l1,r1)+[l2,r2) with O(1)

        Parameters
        ----------
        l1 : int
            left index for first target section
        r1 : int
            right index for first target section
        l2 : int
            left index for second target section
        r2 : int
            right index for second target section
        
        Returns
        -------
        ret : int
            hashed value for [l1,r1)+[l2,r2)
        '''
        h1 = self.calc(l1,r1)
        h2 = self.calc(l2,r2)
        ret = self.connect(h1,r1-l1,h2)
        return ret

from random import randint
# base should be random and greater than max of list
