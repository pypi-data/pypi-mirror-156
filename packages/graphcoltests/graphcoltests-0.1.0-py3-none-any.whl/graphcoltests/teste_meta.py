from graph-col.graph-col.metaheuristicas import Metaheuristicas
import igraph
import numpy as np

def coloracao_viavel(grafo_colorido):
    lista_adj = grafo_colorido.get_adjlist()
    for vertice in range(grafo_colorido.vcount()):
        for vizinho in lista_adj[vertice]:
            assert grafo_colorido.vs[vertice]["cor"] != grafo_colorido.vs[vizinho]["cor"]

grafo = igraph.Graph(6)
grafo.add_edges([(0,1),(0,2),(0,3),(0,4),(0,5),(1,5),(2,3)])

col_tabu = Metaheuristicas.hill_climbing(grafo)

print(coloracao_viavel(col_tabu))
print(col_tabu.vs["cor"])

print(grafo.get_adjlist())

