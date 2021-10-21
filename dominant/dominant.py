import sys, os, time
import networkx as nx

def evaluate(d,g):
    score = 0
    for node in d:
        score += g.nodes[node]['weight']
    return  score

def ratio(g, dominating_set, remaining_nodes):
    rank = {}
    if dominating_set == {}:
        for node in g:
            rank[node] = len(set(g[node]))/g.nodes[node]['weight']
    else:
        for node in remaining_nodes:
            rank[node] = len(set(g[node]) - dominating_set)/g.nodes[node]['weight']
    return rank

def dominant_ratio_per_uncovered_node(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g
        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html
    """
    all_nodes = set(g)
    start_with = sorted(ratio(g,{},{}).items(), key=lambda item: item[1]).pop()[0]
    dominating_set = {start_with}
    dominated_nodes = set(g[start_with])
    remaining_nodes = all_nodes - dominated_nodes - dominating_set
    while remaining_nodes:
        v = sorted(ratio(g,dominated_nodes,remaining_nodes).items(), key=lambda item: item[1]).pop()[0]
        undominated_neighbors = set(g[v]) - dominating_set
        dominating_set.add(v)
        dominated_nodes |= undominated_neighbors
        remaining_nodes -= undominated_neighbors|{v}
    return dominating_set


def dominant_ratio_per_remaining_node(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g
        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html
    """
    all_nodes = set(g)
    start_with = sorted(ratio(g,{},{}).items(), key=lambda item: item[1]).pop()[0]
    dominating_set = {start_with}
    dominated_nodes = set(g[start_with])
    remaining_nodes = all_nodes - dominated_nodes - dominating_set
    while remaining_nodes:
        v = sorted(ratio(g,dominated_nodes,all_nodes - dominating_set).items(), key=lambda item: item[1]).pop()[0]
        undominated_neighbors = set(g[v]) - dominating_set
        dominating_set.add(v)
        dominated_nodes |= undominated_neighbors
        remaining_nodes -= undominated_neighbors|{v}
    return dominating_set


def dominant(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g
        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html
    """
    d = dominant_ratio_per_uncovered_node(g)
    d_min = dominant_ratio_per_remaining_node(g)
    score = evaluate(d,g)
    score_min = evaluate(d_min,g)
    if score_min < score:
        return d_min
    else:
        return d

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
