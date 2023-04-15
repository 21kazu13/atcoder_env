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
        fac = [1,1]
        finv = [1,1]
        inv = [0,1]
        for i in range(2, MAX):
            fac += [fac[-1] * i % P]
            inv += [P - inv[P%i] * (P // i) %P]
            finv += [finv[-1] * inv[i] % P]
    def comb(n,k):
        '''
        Calculate nCk mod P
        Args:
            n (int):0<n<M
            k (int):0<k<=n
        Returns:
            (int): nCk mod P. If conditions are not satisfied, return -1
        '''
        if n < 0 or k < 0 or n < k:
            return -1
        return fac[n] * finv[k] * finv[n-k] % P
