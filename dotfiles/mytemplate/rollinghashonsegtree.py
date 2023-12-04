from atcoder import segtree
class RollingHashOnSegtree():
    '''Calculate and connect Rolling Hash defined by sum(s[i]*base^i) on Segtree
    
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
    
    Methods
    -------
    calc(l,r)
        calculate hash for s[l:r]
    update(idx,v)
        update data for s[idx] to v
    connect(h1,l1,h2)
        calculate hash for concate of h1+h2
    merge(l1,r1,l2,r2)
        calculate hash for [l1,r1)+[l2,r2)
    '''
    def __init__(self, s: list[int], base: int, mod=(1<<61)-1) -> None:
        self.mod = mod
        assert max(s)<base<mod
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
            v=[c*self.pows[idx]%mod for idx,c in enumerate(s)]
        )

    def _op(self, x: int, y: int) -> int:
        return (x+y)%self.mod

    def calc(self, l: int, r: int) -> int:
        '''Calculate hash for [l:r) with O(log(len(s)))

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
        return self.data.prod(l,r)*self.inv[l]%self.mod

    def update(self, idx: int, value: int) -> None:
        '''Update value of s[idx] with O(log(len(s)))

        Parameters
        ----------
        idx : int
            index for target position
        value : int
            update value
        '''
        v = value*self.pows[idx]%self.mod
        self.data.set(idx,v)
    
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
        return (h1+h2*self.pows[len_l1])%self.mod

    def merge(self, l1: int, r1: int, l2: int, r2: int) -> int:
        '''Calculate hash for [l1,r1)+[l2,r2) with O(log(len(s)))

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
