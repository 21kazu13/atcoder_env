#!/usr/bin/env python3

# To visualize graph for tree by using Markdown Preview Enhanced.
# shd101wyy.markdown-preview-enhanced

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

def outDirectedGraph(G: list):
    '''
    input: Directed Graph showed in adjacency list
    output: text formatted to markdown preview enhanced
    '''
    result = ['```dot','digraph G {']
    for num,item in enumerate(G):
        for node in item:
            result.append(f'\t{num} -> {node};')
    result.append('}')
    result.append('```')

    with open('graph.md','w') as f:
        f.write('\n'.join(result))

    return

def outUndirectedGraph(G: list):
    '''
    input: Undirected Graph showed in adjacency list
    output: text formatted to markdown preview enhanced
    '''
    result = ['```dot','graph G {']
    for num,item in enumerate(G):
        for node in item:
            if num <= node:
                result.append(f'\t{num} -- {node};')
    result.append('}')
    result.append('```')

    with open('graph.md','w') as f:
        f.write('\n'.join(result))

    return