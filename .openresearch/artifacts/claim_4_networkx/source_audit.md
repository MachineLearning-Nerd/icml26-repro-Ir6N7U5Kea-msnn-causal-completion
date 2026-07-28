# NetworkX-order source audit

The author repository imports `networkx.algorithms.clique.find_cliques` without
pinning a NetworkX version. On 2026-07-28, the stable NetworkX release was
3.6.1. Its official `networkx/algorithms/clique.py` was retrieved from
`https://raw.githubusercontent.com/networkx/networkx/networkx-3.6.1/networkx/algorithms/clique.py`
with SHA-256
`480bce4406d9ad9f88a5356e11c6ab11342284d7acfa0969362aa867b8448273`.

The current runner transcribes only the iterative `find_cliques` search over an
integer-node adjacency dictionary. It builds the exact block graph used by the
author code and applies the author's strict `d > d_min` update, where
`d=min(number of clique rows, number of clique columns)` for `K=1`.

NetworkX documents clique order as arbitrary. Therefore this is a defensible
released-code route, while the parent exhaustive lexicographic route remains an
independent sensitivity check rather than being erased.
