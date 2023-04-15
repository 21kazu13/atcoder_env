class ModFactorial():
    def __init__(self,M,P):
        '''
        Class for factorial mod p
        Args:
            M (int): maximum value for calculation of factorial
            P (int): modulus. P is required P>M and P is prime.
        Attributes:
            fac (list): fac[i]=i!modP
            finv (list): finv[i]=(i!)^(-1)modP
            inv (list): inv[i]=i^(-1)modP
        '''
        self.P = P
        self.M = M
        self.fac = [1,1]
        self.finv = [1,1]
        self.inv = [0,1]
        for i in range(2, M):
            self.fac += [self.fac[-1] * i % P]
            self.inv += [P - self.inv[P%i] * (P // i) %P]
            self.finv += [self.finv[-1] * self.inv[i] % P]
    def comb(self,n,k):
        '''
        Calculate nCk mod P
        Args:
            n (int):0<n<M
            k (int):0<k<=n
        Returns:
            (int): nCk mod P. If conditions are not satisfied, return -1
        '''
        if n<0 or k<0 or n<k or n>self.M:
            return -1
        return self.fac[n] * self.finv[k] * self.finv[n-k] % self.P
