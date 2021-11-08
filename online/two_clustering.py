import sys, os, time
from statistics import mean
import pandas as pd
import random

##############################################################
####                        UTILS                         ####
##############################################################

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
    return [i % (ring_size//2) for i in range(x-range_size,x+range_size+1)] # Ici i % ring_size//2 car i est une coupe
    
def best_cut(alpha,current_cut,ring_size, range_size=2):
    global global_state

    current_cut_range = range_in_ring(current_cut,ring_size,range_size) #range(ring_size//2) for full range
    cost =[[x, 
            global_state['sigma_count'][x]
            +cost_of_change(alpha,ring_size,current_cut,x)] 
           for x in current_cut_range]
    return tri_2_arg(cost)[0][0]

##############################################################
####                   ALGORITHMS                         ####
##############################################################

def online_two_clustering_LAZY(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme lazy qui change la coupe pour donner -1 à chaque fois 
    """
    # utiliser la variable globale
    global global_state 

    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state = {}
        global_state['sigma'] = [new_msg] #liste des messages
        global_state['sigma_count'] = []  #liste telle que l[index] = nombre de fois où le message index ou index+ring_size//2 est lu
        for i in range(ring_size//2):
            global_state['sigma_count'].append(0)
        global_state['sigma_count'][new_msg%(ring_size//2)]
    else:
        global_state['sigma'].append(new_msg)
        global_state['sigma_count'][new_msg%(ring_size//2)]
        
    current_cut = -1        
    return current_cut # la coupe/2-clusters courante est conservée, ceci n'est pas une solution optimale

def online_two_clustering_ONLINE(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme ONLINE    
    """
    # utiliser la variable globale
    global global_state

    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state = {}
        global_state['sigma'] = [new_msg] #liste des messages
        global_state['sigma_count'] = []  #liste telle que l[index] = nombre de fois où le message index ou index+ring_size//2 est lu
        for i in range(ring_size//2):
            global_state['sigma_count'].append(0)
        global_state['sigma_count'][new_msg%(ring_size//2)] += 1
    else:
        global_state['sigma'].append(new_msg)
        global_state['sigma_count'][new_msg%(ring_size//2)] += 1
    
    if new_msg == current_cut:
        current_cut = best_cut(alpha,current_cut,ring_size, 1) #range de ring_size//4 car on regarde les coupes module ring_size//2  donc ring_size//4 dans chaque sens
    return current_cut

def online_two_clustering_ONLINE_RANDOM(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
        Algorithme ONLINE with a tiny bit of RANDOM   
    """
    # utiliser la variable globale
    global global_state

    # initialiser la variable globale lors du premier appel
    if first_call:
        global_state = {}
        global_state['sigma'] = [new_msg] #liste des messages
        global_state['sigma_count'] = []  #liste telle que l[index] = nombre de fois où le message index ou index+ring_size//2 est lu
        for i in range(ring_size//2):
            global_state['sigma_count'].append(0)
        global_state['sigma_count'][new_msg%(ring_size//2)] += 1
    else:
        global_state['sigma'].append(new_msg)
        global_state['sigma_count'][new_msg%(ring_size//2)] += 1
    
    if new_msg == current_cut:
        current_cut = best_cut(alpha,current_cut,ring_size, 1)
        if random.randint(1,500)==1:
            current_cut = current_cut + 2
    return current_cut 

def online_two_clustering(ring_size, alpha, current_cut, current_cost, new_msg, first_call):
    """
       In use algorithm  
    """
    current_cut = online_two_clustering_ONLINE_RANDOM(ring_size, alpha, current_cut, current_cost, new_msg, first_call)
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