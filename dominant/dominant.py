import sys, os, time
import networkx as nx

#Pour effectuer des tirages aléatoires 
import random

def evaluate(d,g):
    """Pour un sous-ensemble d donné on évalue la somme des poids des nodes"""
    score = 0
    for node in d:
        score += g.nodes[node]['weight']
    return  score

def sort_args(list):
    """Sort list selon 2ème argument"""
    random.shuffle(list)
    return sorted(list, key = lambda x: x[1])

def remove_useless_nodes(S,g,i):
    solution = S
    d = g.nodes(data = "weight", default=1)
    redundant_nodes = []
    for node in S:
        temp_set = S.copy()
        temp_set.remove(node)
        if nx.is_dominating_set(g,temp_set):
            redundant_nodes.append(node)
    if redundant_nodes == []:
        return solution
    else:  
        removed = solution.copy()
        for node in redundant_nodes:
            removed.remove(node)
        if i == 2:
            new_solution = heuristic(removed,g)
        if evaluate(new_solution,g) < evaluate(solution,g):
            solution = new_solution
            solution = remove_useless_nodes(solution,g,i)
        else:
            for i in range(len(redundant_nodes)):
                redundant_nodes[i] = [redundant_nodes[i], d[i]/g.degree(i)]
            redundant_nodes = sort_args(redundant_nodes)
            while redundant_nodes != []:
                node_to_remove = redundant_nodes[-1][0]
                solution.remove(node_to_remove)
                redundant_nodes = []
                for node in S:
                    temp_set = S.copy()
                    temp_set.remove(node)
                    if nx.is_dominating_set(g,temp_set):
                        redundant_nodes.append([node, d[node]/g.degree[node]])
    return solution

def get_isolated_nodes(g):
    solution= []
    for n in g.nodes():
        if g.degree[n] == 0:
            solution.append(n)
    return solution

def heuristic(S,g):
    solution= S.copy()
    candidate_nodes = [node for node in g.nodes() if not node in solution]
    weights = g.nodes(data = "weight", default=1)
    Ws = {}
    Wout = {}
    color = {}
    for node in g.nodes():
        color[node] = 1
    for node in g.nodes():
        if node in solution:
            color[node] = 0
            for i in g.neighbors(node):
                if color[i] == 1:
                    color[i] = -1
    for node in g.nodes():
        Ws[node] = 0
        Wout[node] = 0
        for i in g.neighbors(node):
            if color[i] == 1:
                Ws[node] += weights[i]
                Wout[node] += 1
    isolated_nodes = get_isolated_nodes(g)
    for node in isolated_nodes:
            if not node in solution:
                solution.append(node)
                color[node] = 0
    while not nx.is_dominating_set(g,solution):
        node_list_score = []
        max_score = 0
        for node in candidate_nodes:
            score = (Ws[node] + weights[node] * color[node])/(weights[node])
            if score > max_score:
                max_score = score
            node_list_score.append([node,score])
        best_nodes = [i for i in node_list_score if i[1] == max_score]
        if len(best_nodes) == 1:
            new_node = best_nodes[-1][0]
        else:
            for i in best_nodes:
                i[1] = (Wout[i[0]] + color[i[0]])/weights[i[0]]
            best_nodes = sort_args(best_nodes)
            new_node = best_nodes[-1][0]        
        solution.append(new_node)
        candidate_nodes.remove(new_node)
        color[new_node] = 0 #Le sommet choisi devient noir
        for i in g.neighbors(new_node):
            if color[i] ==1:
                color[i] = -1
                for j in g.neighbors(i):
                    Ws[j] -= weights[i]
                    Wout[j] -= 1 
    solution= remove_useless_nodes(solution,g,2)
    return solution

def randomize_dominant(g, proportion_to_delete, rounds):
    """randomily reconstruct part of the dominant solution"""
    S = heuristic([],g) 
    for i in range(rounds):
        infeasible_S = S.copy()
        number_of_nodes_to_del = int(proportion_to_delete*len(infeasible_S))
        for j in range(number_of_nodes_to_del):
            infeasible_S.pop(random.randint(0,len(infeasible_S)-1))
        new_S = heuristic(infeasible_S,g)
        if evaluate(new_S,g) < evaluate(S,g):
            S = new_S
    return S

def dominant(g):
    """
        A Faire:         
        - Ecrire une fonction qui retourne le dominant du graphe non dirigé g passé en parametre.
        - cette fonction doit retourner la liste des noeuds d'un petit dominant de g

        :param g: le graphe est donné dans le format networkx : https://networkx.github.io/documentation/stable/reference/classes/graph.html
    """
    solution= randomize_dominant(g, 0.5, 25)
    return solution

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

    score = 0

    for graph_filename in sorted(os.listdir(input_dir)):
        # importer le graphe
        g = load_graph(os.path.join(input_dir, graph_filename))

        # calcul du dominant
        D = sorted(dominant(g), key=lambda x: int(x))

        #Score
        score += evaluate(D,g)

        # ajout au rapport
        output_file.write(graph_filename)
        for node in D:
            output_file.write(' {}'.format(node))
        output_file.write('\n')

    print("The final score is: " + str(score))
    output_file.close()
