import sys, os, time
import networkx as nx

#Pour effectuer des tirages aléatoires de sommets dans les construction de solution greedy ou naïves
import random
from networkx.algorithms.assortativity import neighbor_degree

from networkx.algorithms.bipartite.matrix import from_biadjacency_matrix
from networkx.algorithms.clique import number_of_cliques


def W(S,g):
    """Pour une solution S donnée calcule la somme des poids des sommets"""
    res = 0
    weight = g.nodes(data = "weight", default=1)
    for node in S:
        res += weight[node]
    return res


def tri_2_arg(list):
    """Prend une liste de couple (a,b) et la trie selon les valeurs de b dans l'ordre croissant"""
    random.shuffle(list)
    return sorted(list, key = lambda x: x[1])



def remove_useless_nodes(S,g,i):

    res = S
    d = g.nodes(data = "weight", default=1)
    redundant_nodes = []
    for node in S:
        temp = S.copy()
        temp.remove(node)
        if nx.is_dominating_set(g,temp):
            redundant_nodes.append(node)

    if redundant_nodes == []:
        return res

    else:
    
        removed = res.copy()
        for node in redundant_nodes:
            removed.remove(node)

        if i == 2:
            new_res = H2(removed,g)
            
        if i == 3: 
            new_res = H3(removed,g)
            
        if i == 4: 
            new_res = H4(removed,g)
            
        if i == 5: 
            new_res = H5(removed,g)

        if W(new_res,g) < W(res,g):
            res = new_res
            res = remove_useless_nodes(res,g,i)
        else:
            for i in range(len(redundant_nodes)):
                redundant_nodes[i] = [redundant_nodes[i], d[i]/g.degree(i)]
            redundant_nodes = tri_2_arg(redundant_nodes)
            while redundant_nodes != []:
                node_to_remove = redundant_nodes[-1][0]
                res.remove(node_to_remove)
                redundant_nodes = []
                for node in S:
                    temp = S.copy()
                    temp.remove(node)
                    if nx.is_dominating_set(g,temp):
                        redundant_nodes.append([node, d[node]/g.degree[node]])
          

    return res


def get_isolated_nodes(g):
    res = []
    for n in g.nodes():
        if g.degree[n] == 0:
            res.append(n)
    return res

def H2(S,g):

    res = S.copy()

    candidate_nodes = [node for node in g.nodes() if not node in res]


    weight = g.nodes(data = "weight", default=1)

    Ws = {}
    Wout = {}
    color = {}

    for node in g.nodes():
        color[node] = 1

    for node in g.nodes():
        if node in res:
            color[node] = 0
            for i in g.neighbors(node):
                if color[i] == 1:
                    color[i] = -1
    for node in g.nodes():
        Ws[node] = 0
        Wout[node] = 0
        for i in g.neighbors(node):
            if color[i] == 1:
                Ws[node] += weight[i]
                Wout[node] += 1

    isolated_nodes = get_isolated_nodes(g)

    for node in isolated_nodes:
            if not node in res:
                res.append(node)
                color[node] = 0
   

    while not nx.is_dominating_set(g,res):
        node_list_score = []
        max_score = 0
        for node in candidate_nodes:
            score = (Ws[node] + weight[node] * color[node])/(weight[node])
            if score > max_score:
                max_score = score
            node_list_score.append([node,score])
        
        best_nodes = [i for i in node_list_score if i[1] == max_score]

        if len(best_nodes) == 1:
            new_node = best_nodes[-1][0]
        else:
            for i in best_nodes:
                i[1] = (Wout[i[0]] + color[i[0]])/weight[i[0]]
            best_nodes = tri_2_arg(best_nodes)
            new_node = best_nodes[-1][0]        
        
        res.append(new_node)

        candidate_nodes.remove(new_node)

        color[new_node] = 0 #Le sommet choisi devient noir

        for i in g.neighbors(new_node):
            if color[i] ==1:
                color[i] = -1
                for j in g.neighbors(i):
                    Ws[j] -= weight[i]
                    Wout[j] -= 1 
        


    res = remove_useless_nodes(res,g,2)
    
    return res

def H3(S,g):
    res = S.copy()

    candidate_nodes = list(g.nodes())

    for node in res:
        candidate_nodes.remove(node)

    weight = g.nodes(data = "weight", default=1)

    Ws = {}
    Wout = {}
    color = {}
    deg = {}

    for node in g.nodes():
        color[node] = 1

    for node in g.nodes():
        if node in res:
            color[node] = 0
            for i in g.neighbors(node):
                if color[i] == 1:
                    color[i] = -1
        else:
            color[node] = 1
    for node in g.nodes():
        Ws[node] = 0
        Wout[node] = 0
        deg[node] = g.degree[node]
        for i in g.neighbors(node):
            if color[i] == 1:
                Ws[node] += weight[i]
                Wout[node] += 1

    isolated_nodes = get_isolated_nodes(g)

    for node in isolated_nodes:
            if not node in res:
                res.append(node)
                color[node] = 0
   

    while not nx.is_dominating_set(g,res):
        node_list_score = []
        max_score = 0
        for node in candidate_nodes:
            score = (Ws[node] + weight[node] * color[node])/(weight[node])
            if score > max_score:
                max_score = score
            node_list_score.append([node,score])
        
        best_nodes = [i for i in node_list_score if i[1] == max_score]

        if len(best_nodes) == 1:
            new_node = best_nodes[-1][0]
        else:
            white_best_nodes = []
            for i in best_nodes:
                if color[i[0]] == 1:
                    white_best_nodes.append(i)
            if len(white_best_nodes) == 1:
                new_node =  white_best_nodes[-1][0]
            elif len(white_best_nodes) > 1:
                for i in white_best_nodes:
                    i[1] = deg[i[0]]
                white_best_nodes = tri_2_arg(white_best_nodes)
                new_node = white_best_nodes[0][0]
            else: # pas de sommet blanc
                new_node = best_nodes[random.randint(0, len(best_nodes)-1)][0]

        
        res.append(new_node)

        candidate_nodes.remove(new_node)

        color[new_node] = 0 #Le sommet choisi devient noir

        for i in g.neighbors(new_node):
            if color[i] == 1:
                color[i] = -1 #Ses voisins deviennent gris
        
        for node in g.nodes():
            Ws[node]=0
            Wout[node]=0
            for i in g.neighbors(node):
                if color[i] == 1:
                    Ws[node] += weight[i]
                    Wout[node] += 1

    res = remove_useless_nodes(res,g,3)

    return res





def H4(S,g):
    """Crée une solution de manière glouton
    """

    res = S.copy()

    candidate_nodes = list(g.nodes())

    for node in res:
        candidate_nodes.remove(node)

    weight = g.nodes(data = "weight", default=1)

    Ws = {}
    Wout = {}
    color = {}
    deg = {}

    for node in g.nodes():
        color[node] = 1

    for node in g.nodes():
        if node in res:
            color[node] = 0
            for i in g.neighbors(node):
                if color[i] == 1:
                    color[i] = -1
        else:
            color[node] = 1
    for node in g.nodes():
        Ws[node] = 0
        Wout[node] = 0
        deg[node] = g.degree[node]
        for i in g.neighbors(node):
            if color[i] == 1:
                Ws[node] += weight[i]
                Wout[node] += 1

    isolated_nodes = get_isolated_nodes(g)

    for node in isolated_nodes:
            if not node in res:
                res.append(node)
                color[node] = 0
   

    while not nx.is_dominating_set(g,res):
        

        exist = False
        for n in g.nodes():
            if color[n] == 1:
                no_white_neigh = True
                non_black_neigh = 0
                for i in g.neighbors(n):
                    if color[i] == 1:
                        no_white_neigh = False
                    if color[i] != 0:
                        non_black_neigh += 1
                        m = i
                if no_white_neigh and non_black_neigh == 1:
                    u = n
                    v = m
                    exist = True

        if exist:
            score_u = (Ws[u] + weight[u] * color[u])/(weight[u])
            score_v = (Ws[v] + weight[v] * color[v])/(weight[v])

            if score_u > score_v:
                new_node = u
            else:
                new_node = v

        else:
        
            node_list_score = []
            max_score = 0
            for node in candidate_nodes:
                score = (Ws[node] + weight[node] * color[node])/(weight[node])
                if score > max_score:
                    max_score = score
                node_list_score.append([node,score])
            
            best_nodes = [i for i in node_list_score if i[1] == max_score]

            if len(best_nodes) == 1:
                new_node = best_nodes[-1][0]
            else:
                for i in best_nodes:
                    i[1] = (Wout[i[0]] + color[i[0]])/weight[i[0]]
                best_nodes = tri_2_arg(best_nodes)
                new_node = best_nodes[-1][0]        
        
        res.append(new_node)

        candidate_nodes.remove(new_node)

        color[new_node] = 0 #Le sommet choisi devient noir

        for i in g.neighbors(new_node):
            if color[i] == 1:
                color[i] = -1 #Ses voisins blancs deviennent gris
        
        for node in g.nodes():
            Ws[node]=0
            Wout[node]=0
            for i in g.neighbors(node):
                if color[i] == 1:
                    Ws[node] += weight[i]
                    Wout[node] += 1

    res = remove_useless_nodes(res,g,4)
    
    return res


def H5(S,g):
    res = S

    candidate_nodes = list(g.nodes())

    for node in res:
        candidate_nodes.remove(node)

    weight = g.nodes(data = "weight", default=1)

    Ws = {}
    Wout = {}
    color = {}
    deg = {}

    for node in g.nodes():
        color[node] = 1

    for node in g.nodes():
        if node in res:
            color[node] = 0
            for i in g.neighbors(node):
                if color[i] == 1:
                    color[i] = -1

        else:
            color[node] = 1
    for node in g.nodes():
        Ws[node] = 0
        Wout[node] = 0
        deg[node] = g.degree[node]
        for i in g.neighbors(node):
            if color[i] == 1:
                Ws[node] += weight[i]
                Wout[node] += 1

    isolated_nodes = get_isolated_nodes(g)

    for node in isolated_nodes:
            if not node in res:
                res.append(node)
                color[node] = 0
   

    while not nx.is_dominating_set(g,res):
        

        exist = False
        for n in g.nodes():
            if color[n] == 1:
                no_white_neigh = True
                non_black_neigh = 0
                for i in g.neighbors(n):
                    if color[i] == 1:
                        no_white_neigh = False
                    if color[i] != 0:
                        non_black_neigh += 1
                        m = i
                if no_white_neigh and non_black_neigh == 1:
                    u = n
                    v = m
                    exist = True

        if exist:
            score_u = (Ws[u] + weight[u] * color[u])/(weight[u])
            score_v = (Ws[v] + weight[v] * color[v])/(weight[v])

            if score_u > score_v:
                new_node = u
            else:
                new_node = v

        else:
        
            node_list_score = []
            max_score = 0
            for node in candidate_nodes:
                score = (Ws[node] + weight[node] * color[node])/(weight[node])
                if score > max_score:
                    max_score = score
                node_list_score.append([node,score])
        
            best_nodes = [i for i in node_list_score if i[1] == max_score]

            if len(best_nodes) == 1:
                new_node = best_nodes[-1][0]
            else:
                white_best_nodes = []
                for i in best_nodes:
                    if color[i[0]] == 1:
                        white_best_nodes.append(i)
                if len(white_best_nodes) == 1:
                    new_node =  white_best_nodes[-1][0]
                elif len(white_best_nodes) > 1:
                    for i in white_best_nodes:
                        i[1] = deg[i[0]]
                    white_best_nodes = tri_2_arg(white_best_nodes)
                    new_node = white_best_nodes[0][0]
                else: # pas de sommet blanc
                    new_node = best_nodes[random.randint(0, len(best_nodes)-1)][0]        
        
        res.append(new_node)

        candidate_nodes.remove(new_node)

        color[new_node] = 0 #Le sommet choisi devient noir

        for i in g.neighbors(new_node):
            if color[i] == 1:
                color[i] = -1 #Ses voisins blancs deviennent gris
        
        for node in g.nodes():
            Ws[node]=0
            Wout[node]=0
            for i in g.neighbors(node):
                if color[i] == 1:
                    Ws[node] += weight[i]
                    Wout[node] += 1

    res = remove_useless_nodes(res,g,5)
    
    return res


def solve_dom_randomized(g):
    """Construit et déstruit en partie les solutions créées par l'algorithme H2 (qui est le plus rapide) en boucle tout en gardant le meilleur dominant au fur et a mesure."""
    S = H2([],g) 
    proportion_to_del =  0.5
    for i in range(25):
        infeasible_S = S.copy()
        number_of_nodes_to_del = int(proportion_to_del*len(infeasible_S))
        for k in range(number_of_nodes_to_del):
            infeasible_S.pop(random.randint(0,len(infeasible_S)-1))
        new_S = H2(infeasible_S,g)
        if W(new_S,g) < W(S,g):
            S = new_S
    return S


def dominant(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html

    """
    res = solve_dom_randomized(g)


    return res

   


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
