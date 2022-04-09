#!/usr/bin/env python3

# To visualize graph for tree by using Markdown Preview Enhanced.
# shd101wyy.markdown-preview-enhanced

# References
## https://shd101wyy.github.io/markdown-preview-enhanced/#/diagrams
## https://graphviz.org/doc/info/lang.html
## https://ja.wikipedia.org/wiki/DOT%E8%A8%80%E8%AA%9E

## できればクラス化したいな...
## http://pineplanter.moo.jp/non-it-salaryman/2018/09/04/python-external-class/
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

def outDirectedGraph(G: list,s='graph'):
    '''
    input: Directed Graph showed in adjacency list
    output: text formatted to markdown preview enhanced
    '''
    result = ['```dot','digraph G {']
    for num,item in enumerate(G):
        if len(item)==0:
            result.append(f'\t{num};')
            continue
        for node in item:
            result.append(f'\t{num} -> {node};')
    result.append('}')
    result.append('```')

    with open(s+'.md','w') as f:
        f.write('\n'.join(result))

    return

def outUndirectedGraph(G: list,s='graph'):
    '''
    input: Undirected Graph showed in adjacency list
    output: text formatted to markdown preview enhanced
    '''
    result = ['```dot','graph G {']
    for num,item in enumerate(G):
        if len(item)==0:
            result.append(f'\t{num};')
            continue
        for node in item:
            if num <= node:
                result.append(f'\t{num} -- {node};')
    result.append('}')
    result.append('```')

    with open(s+'.md','w') as f:
        f.write('\n'.join(result))

    return