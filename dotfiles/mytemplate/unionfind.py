from collections import defaultdict

class UnionFind():
    def __init__(self, n):
        '''
        Class for union find
        Args:
            n (int): number of nodes
        Attributes:
            n (int): number of nodes
            parents (list): parent of each nodes. If nodes are root, it returns negative value and its absolute value is member count.
            group_count (int): number of groups in UF
        '''
        self.n = n
        # parents[m]が非負整数であれば親のnodeを示す
        # 負であればrootであることを示し、その絶対値は自分を含んだ要素数を示す
        # unionメソッドでどっちにくっつけるかの判定に用いる
        self.parents = [-1] * n
        self.group_count = n

    def isroot(self,x):
        '''
        Check if node is root: O(1)
        Args:
            x (int): node number
        Returns:
            bool: True if node is root. False if node is not root.
        '''
        return True if self.parents[x] < 0 else False
    
    def find(self, x):
        '''
        Find root for node: O(a(n))
        Args:
            x (int): node number
        Returns:
            int: root number of node x
        '''
        if self.parents[x] < 0:
            # 負であればrootなのでrootのnode番号を返す
            return x
        else:
            # 正であればその親のnodeを探す
            # その際parents[x]の値をroot直通にする
            # 経路圧縮
            self.parents[x] = self.find(self.parents[x])
            return self.parents[x]

    def union(self, x, y):
        '''
        Union two nodes into one group
        Args:
            x (int): node number
            y (int): node number
        Returns:
            Nothing
        '''
        # x,yそれぞれのrootを見つけ、置き換える
        x = self.find(x)
        y = self.find(y)
        
        # 同一であれば何もしない
        if x == y:
            return

        # 異なっていれば、サイズの大きい方に小さい方をくっつける
        # findの経路圧縮をできるだけ少なく(計算し直すものが少なくなる)できるようなイメージ
        # x,yはrootなので、yの方がサイズ数が大きい(負なので値としては小さくなる)場合はx,yをswap
        if self.parents[x] > self.parents[y]:
            x, y = y, x
        # xにyをくっつけ(サイズの更新)、yの親をに置き換える
        self.parents[x] += self.parents[y]
        self.parents[y] = x
        self.group_count -= 1

    def same(self, x, y):
        '''
        Confirm two nodes have same root or not
        Args:
            x (int): node number
            y (int): node number
        Returns:
            (bool): True in case both have the same root, False in the other case.
        '''
        # rootを探して同一ならtrue
        return self.find(x) == self.find(y)

    def size(self, x):
        '''
        Get the group size in x
        Args:
            x (int): node number
        Returns:
            (int): Size (member count) in the group of x
        '''
        # rootを探して格納されている要素数を返す
        return -self.parents[self.find(x)]

    def members(self, x):
        '''
        Get the all group members in x: O(n)
        Args:
            x (int): node number
        Returns:
            (list): nodes who are in group of x
        '''
        root = self.find(x)
        return [i for i in range(self.n) if self.find(i) == root]

    def roots(self):
        '''
        Get all roots in UF: O(n)
        Args:
            Nothing
        Returns:
            (list): list which all roots includes in
        '''
        return [i for i, x in enumerate(self.parents) if x < 0]

    def all_group_members(self):
        # 各rootに対してそれに属するnodeをdict形式で格納する
        # 存在しないkeyを渡すと[]が取得でき格納されるdict
        group_members = defaultdict(list)
        # 各nodeに対してどのrootに属しているかを
        for member in range(self.n):
            #group_members[nodeのroot]がリストなので、それに対してnodeを追加する
            group_members[self.find(member)].append(member)
        return group_members

    def __str__(self):
        # 上で求めたdict形式の可視化
        # __str__のオーバーライドなのでprint(instance)がこの形式で出力される
        # root: [node,node,...]
        return '\n'.join(f'{r}: {m}' for r, m in self.all_group_members().items())
