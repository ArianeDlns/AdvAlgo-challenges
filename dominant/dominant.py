import sys, os, time
import networkx as nx

def order_graph(g) :
    """
    sort the graph according to the succession of nodes
    """
    first_node = list(g.nodes)[0] 
    new_graph = [first_node] 
    new_graph.append(list(g[first_node])[0]) 
    while len(new_graph) != g.order() :
        adjacent = list(g[new_graph[-1]]) 
        adjacent.remove(new_graph[-2]) 
        new_graph.append(adjacent[0]) 
    return new_graph

def cycle_dominant(g):
    dominant_set = set()
    ordered_graph = order_graph(g)
    for i in range(0, len(ordered_graph), 3):
        dominant_set.add(ordered_graph[i])
    return dominant_set

def dominant(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g
        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html
    """
    all_nodes = set(g)
    adjacent_nb = {} 
    for node in all_nodes :
        adjacent_nb[g.degree[node]] = node
    if len(adjacent_nb) == 1 and (g.number_of_nodes() == g.number_of_edges()) : 
        return cycle_dominant(g)
    else :
        max_adjacent = max(adjacent_nb.keys()) 
        max_node = adjacent_nb[max_adjacent]        
        dominating_set = {max_node}
        not_selected = all_nodes - {max_node} 
        all_nodes = all_nodes - set(g[max_node]) - {max_node} 
        g = g.subgraph(not_selected) 
        while all_nodes :
            adjacent_nb = {} 
            for node in not_selected :
                remaining_adjacent = []
                for node2 in list(g[node]) :
                    if node2 in all_nodes :
                        remaining_adjacent.append(node2)
                adjacent_nb[len(remaining_adjacent)] = node
            if len(adjacent_nb) == 1 and (g.number_of_nodes() == g.number_of_edges()) :
                dominating_set |= cycle_dominant(g)
                return dominating_set
            max_adjacent = max(adjacent_nb.keys())
            max_node = adjacent_nb[max_adjacent]
            dominating_set.add(max_node)
            not_selected = not_selected - {max_node}
            all_nodes = all_nodes - set(g[max_node]) - {max_node}
            g = g.subgraph(not_selected)
    return dominating_set

#########################################
#### Ne pas modifier le code suivant ####
#########################################

def load_graph(name):
    with open(name, "r") as f:
        state = 0
        G = None
        for l in f:
            if state == 0:  # Header nb of nodes
                state = 1
            elif state == 1:  # Nb of nodes
                nodes = int(l)
                state = 2
            elif state == 2:  # Header position
                i = 0
                state = 3
            elif state == 3:  # Position
                i += 1
                if i >= nodes:
                    state = 4
            elif state == 4:  # Header node weight
                i = 0
                state = 5
                G = nx.Graph()
            elif state == 5:  # Node weight
                G.add_node(i, weight=int(l))
                i += 1
                if i >= nodes:
                    state = 6
            elif state == 6:  # Header edge
                i = 0
                state = 7
            elif state == 7:
                if i > nodes:
                    pass
                else:
                    edges = l.strip().split(" ")
                    for j, w in enumerate(edges):
                        w = int(w)
                        if w == 1 and (not i == j):
                            G.add_edge(i, j)
                    i += 1

        return G


#########################################
#### Ne pas modifier le code suivant ####
#########################################
if __name__ == "__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])

    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(input_dir, "doesn't exist")
        exit()

    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    for graph_filename in sorted(os.listdir(input_dir)):
        # importer le graphe
        g = load_graph(os.path.join(input_dir, graph_filename))

        # calcul du dominant
        D = sorted(dominant(g), key=lambda x: int(x))

        # ajout au rapport
        output_file.write(graph_filename)
        for node in D:
            output_file.write(' {}'.format(node))
        output_file.write('\n')

    output_file.close()
