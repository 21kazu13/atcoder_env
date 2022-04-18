#!/usr/bin/env python3

# To visualize graph for tree by using Markdown Preview Enhanced.
# shd101wyy.markdown-preview-enhanced

# References
## https://shd101wyy.github.io/markdown-preview-enhanced/#/diagrams
## https://graphviz.org/doc/info/lang.html
## https://ja.wikipedia.org/wiki/DOT%E8%A8%80%E8%AA%9E

'''
Required format for directed graph by markdown preview enhanced is here:
* for undirected graph, place 'graph' and '--' instead of 'digraph' and '->'
```dot
digraph G {
    A -> B;
    B -> C;
    B -> D;
}
```

'''
class VisualGraph:
    '''
    - Check basic contents of graph structure
    - Generate markdown file for visualization
    '''
    def __init__(self, G: list, hasdirection=False, weightcolumn=0) -> None:
        self.neighborList = G
        self.numberOfNodes = len(G)
        # 0: no cost of edges, 1: has cost of edges: 
        self.hasWeight = 0 if type(G[0][0]) == int else 1
        self.hasDirection = 0 if not hasdirection else 1
        self.weightColumn = weightcolumn
        self.numberOfEdges = sum([len(G[i]) for i in range(self.numberOfNodes)])
        self.expressionOfEdges = '->'
        if not self.hasDirection:
            self.numberOfEdges //= 2
            self.expressionOfEdges = '--'
    
    def __str__(self) -> str:
        type = 'directed' if self.hasDirection else 'undirected'
        res = f'This is {type} graph.\n'
        res += f'  Number of Nodes: {self.numberOfNodes}\n'
        res += f'  Number of Edges: {self.numberOfEdges}\n'
        return res

    def _generateHeadFoot(self) -> tuple:
        headers = ['```dot','graph G{']
        if self.hasDirection:
            headers[1] = 'digraph G{'
        footers = ['}','```']
        return (headers,footers)

    def _extractDestCost(self, org: int, node) -> tuple:
        if self.hasWeight:
            cost = node[self.weightColumn]
            dest = node[self.weightColumn^1]
            ex = f'\t{org} {self.expressionOfEdges} {dest} [label="{cost}"];'
        else:
            dest = node
            cost = ''
            ex = f'\t{org} {self.expressionOfEdges} {dest};'
        return (dest,ex)


    def generateMarkdown(self,filename='graph') -> None:
        headers, footers = self._generateHeadFoot()
        res = []
        for org,item in enumerate(self.neighborList):
            if len(item)==0:
                res.append(f'\t{org};')
                continue
            for node in item:
                dest, expression = self._extractDestCost(org,node)
                if org > dest and not self.hasDirection:
                    continue
                res.append(expression)
                with open(filename+'.md','w') as f:
                    f.write('\n'.join(headers+res+footers))
        return
