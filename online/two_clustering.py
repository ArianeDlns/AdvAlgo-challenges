import sys, os, time
from statistics import mean
import pandas as pd
import random

##############################################################
####                        UTILS                         ####
##############################################################
def _overall_best_cut(sigma,alpha):
    cost = pd.DataFrame([[x,sigma.count(x)] for x in range(ring_size)], columns=['node','cost'])
    cost = pd.merge(cost[0:int(ring_size/2)],cost[int(ring_size/2):].reset_index(drop=True),right_index=True,left_index=True)
    cost['message_cost'] = cost['cost_x'] + cost['cost_y']
    cost = cost[['node_x','message_cost']]
    cost['change'] = 2*alpha*pd.concat([abs((ring_size//2)-cost['node_x']), cost['node_x']], axis=1).min(axis=1)
    cost['added_value'] = cost['change']+cost['message_cost']
    cost = cost.sort_values('added_value')
    return(cost['node_x'].iloc[0],cost['added_value'].iloc[0])

def cost_of_change(alpha,ring_size,current_cut,next_cut):
    """Computes the cost of change from one cut to another"""
    current_cut = current_cut % (ring_size//2)
    next_cut = next_cut % (ring_size//2)
    if current_cut < next_cut:
        online_cost = 2*alpha*min(next_cut-current_cut, current_cut+(ring_size//2)-next_cut)
    elif current_cut > next_cut:
        online_cost = 2*alpha*min(current_cut-next_cut, next_cut+(ring_size//2)-current_cut)
    else:
        online_cost = 0
    return online_cost
                
def tri_2_arg(list):
    """Prend une liste de couple (a,b) et la trie selon les valeurs de b dans l'ordre croissant"""
    random.shuffle(list)
    return sorted(list, key = lambda x: x[1])

def range_in_ring(x,ring_size,range_size):
    """Retourne la liste des 2*range_size nodes du ring adjacents à x"""
    return [i % ring_size for i in range(x-range_size,x+range_size)]
    
def offline_best_cut(sigma,alpha,current_cut,ring_size):
    current_cut_range = range_in_ring(current_cut,ring_size,3) #range(ring_size//2) for full range
    cost =[[x, 
            sigma.count(x%ring_size)
            +sigma.count((x+ring_size//2)%ring_size)
            +cost_of_change(alpha,ring_size,current_cut,x)] 
           for x in current_cut_range]
    return tri_2_arg(cost)[0]

# variable globale qui peut servir à stocker des informations d'un appel à l'autre si besoin
global_state = 0 

def online_two_clustering_KNOWING(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme qui connait les best coupes initiale pour chacune des instances (il s'agit d'un greedy offline)
        Sert de baseline

        :param ring_size: taille de l'anneau
        :param alpha: ...
        :param current_cut: indice dans range(ring_size//2) représentant la coupe courante
        :param current_cost: coût courant accumulé depuis le début
        :param new_msg: indice dans range(ring_size) représentant le noeud de départ du nouveau message
        :param first_call: booléen qui permet de reconnaitre le premier message  
        :return l'indice dans range(ring_size//2) représentant la nouvelle coupe     
    """
    # known best_cuts
    best_cuts = [0, 254, 255, 0, 63, 255, 0, 2, 22, 63, 6, 255, 0, 0, 255]
    # utiliser la variable globale
    global global_state 
    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state += 1
    current_cut = best_cuts[int((global_state-1)/10)]
    return current_cut 

def online_two_clustering_LAZY(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme lazy qui change la coupe pour donner -1 à chaque fois 
    """
    # utiliser la variable globale
    global global_state 

    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state = {}
    current_cut = -1        
    return current_cut # la coupe/2-clusters courante est conservée, ceci n'est pas une solution optimale

def online_two_clustering_GREEDY(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme greedy    
    """
    # utiliser la variable globale
    global global_state 

    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state = [new_msg]
    else:
        global_state += [new_msg]
    
    if new_msg == current_cut:
        current_cut = offline_best_cut(list(global_state),alpha,current_cut,ring_size)[0]
    return current_cut 

def online_two_clustering(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
       In use algorithm  
    """
    current_cut = online_two_clustering_GREEDY(ring_size, alpha, current_cut, current_cost, new_msg, first_call)
    return current_cut

##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
if __name__=="__main__":
    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()
    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(output_dir, "doesn't exist")
        exit()       
    
    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))             
    output_file = open(os.path.join(output_dir, output_filename), 'w')
    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        # importer l'instance depuis le fichier (attention code non robuste)
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        ring_size = int(lines[1])
        alpha = int(lines[4])
        sigma = [int(d) for d in lines[7].split()]
                
        # lancement de l'algo online 10 fois et calcul du meilleur cout
        nb_runs = 10
        best_cost = float('inf')
        for _ in range(nb_runs):
            online_cost = 0
            current_cut = 0
            first_call = True
            for msg in sigma:
                next_cut = online_two_clustering(ring_size, alpha, current_cut, online_cost, msg, first_call) % (ring_size//2)
                if current_cut < next_cut:
                    online_cost += 2*alpha*min(next_cut-current_cut, current_cut+(ring_size//2)-next_cut)
                if current_cut > next_cut:
                    online_cost += 2*alpha*min(current_cut-next_cut, next_cut+(ring_size//2)-current_cut)
                
                current_cut = next_cut
                if current_cut == msg % (ring_size//2):
                    online_cost += 1
                first_call = False
            best_cost = min(best_cost, online_cost)
        scores.append(best_cost)
        # ajout au rapport
        output_file.write(instance_filename + ': score: {}\n'.format(best_cost))
    output_file.write('score total: ' + str(sum(scores)))
    output_file.close()