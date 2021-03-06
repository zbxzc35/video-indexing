from scipy.cluster.hierarchy import ward, dendrogram, linkage, fcluster
import copy
import math
import json
import os

import matplotlib
import matplotlib.pyplot as plt
try:
    plt.style.use('ggplot')
except:
    pass

import sys
import math
import numpy as np

def getCosSimilarty(a_dict, b_dict):
    
    space = list(set(a_dict.keys()) | set(b_dict.keys()))
    
    # compute consine similarity (a dot b/ |a| * |b|)
    sumab = 0.0
    sumaa = 0.0
    sumbb = 0.0

    for dim in space:

        a = 0.0
        b = 0.0
        if dim in a_dict:
            a = a_dict[dim]
        if dim in b_dict:
            b = b_dict[dim]

        sumab += a * b
        sumaa += a * a
        sumbb += b * b        
    
    return sumab/(math.sqrt(sumaa * sumbb))

'''
Input: video_name
Output: term frequency for each frame (a list of (frame_number, tf) pairs)
'''
def load_turker_labels(video_name, turker_label_folder = "/home/t-yuche/gt-labeling/turker-labels"):

    video_folder = os.path.join(turker_label_folder, video_name)
    fs = sorted(os.listdir(video_folder), key=lambda key: int(key.split('.')[0]))

    all_nodes = [] 
    for frame_name in fs:
        
        label_path = os.path.join(video_folder, frame_name)
        labels = json.load(open(label_path))['gt_labels']
    
        #TODO: consider hierarchical words         
        ws = {}
        for choices in labels:
            for choice in choices:
                if choice not in ws:
                    ws[choice] = 1
                else:
                    ws[choice] += 1
        all_nodes += [(int(frame_name.split('.')[0]) ,ws)]

    return all_nodes



def getConstrainedPairwiseDist(clusters, pair_range = 1E+10):
    
    darray = np.empty([len(clusters), len(clusters)], dtype=float)
    darray.fill(np.inf)

    # for all the nodes that are active
    active_nodes = filter(lambda x: x['active'] == True,  clusters)

    # check nodes that are within range
    for a_idx, a_node in enumerate(active_nodes):
        for b_idx in xrange(len(active_nodes)):
            
            if a_idx == b_idx:
                continue
            
            b_node = active_nodes[b_idx] 

            # TODO: other constraints? 
            within_range = False
            for i in a_node['n_idx']:
                for j in b_node['n_idx']:
                    assert( i != j )
                    if i != j and  abs(i-j) <= pair_range:
                        within_range = True
                        break

            if within_range:
                dist = 1.0 - getCosSimilarty(a_node['tf'], b_node['tf']) 
                darray[a_node['idx'], b_node['idx']] = dist

    return darray 

def getActiveClusterNum(clusters):
    
    active_nodes = filter(lambda x: x['active'] == True,  clusters)

    return len(active_nodes)

def cluster(all_nodes, num_clusters = 1): 
    
    # all_nodes: a list of (frame_timestamp, tf)s, should be sorted by frame_timestamp
    clusters = []

    # initialize clusters
    for idx, node in enumerate(all_nodes):
        time_stamp = node[0] # int frame number
        tf = node[1] # {desk:1, table:2}
        c = {}
        c['idx'] = idx
        c['ts'] = [time_stamp]
        c['n_idx'] = [idx]
        c['tf'] = tf
        c['active'] = True
        c['descs'] = []
        clusters += [c]
   
 
    linkage_matrix = []
    k = len(clusters)
    while getActiveClusterNum(clusters) > max(1, num_clusters):
        
        # get pairwise distance
        darray = getConstrainedPairwiseDist(clusters, 1)
 
        # merge the two closest clusters
        # get the metric index of the minimum number
        a_idx, b_idx = np.unravel_index(np.argmin(darray), darray.shape)
        dist = np.min(darray)

        # create new cluster
        # merge node a and b
        k -= 1
        a_node = clusters[a_idx]
        b_node = clusters[b_idx] 
        
        #print 'c = ', len(clusters), 'k =', k  , 'merge:', a_node['idx'], 'and',  b_node['idx'], '(', a_idx, '/' , b_idx, ')'

        c = {}
        c['idx'] = len(clusters)
        c['ts'] = sorted(a_node['ts'] + b_node['ts']) # combining two ts lists
        c['n_idx'] = sorted(a_node['n_idx'] + b_node['n_idx']) 
        
        # merge two term freq
        tf = copy.deepcopy(a_node['tf'])
        for key in b_node['tf']:
            if key not in tf:
                tf[key] = b_node['tf'][key]
            else:
                tf[key] += b_node['tf'][key]

        c['tf'] = tf 
        c['active'] = True
        c['descs'] = [a_node['idx'] , b_node['idx']]
        clusters += [c]

        # disable merged cluster
        clusters[a_idx]['active'] = False
        clusters[b_idx]['active'] = False
        #print c

        # update cluster (linkage_matrix)  append [clusterID_1, clusterID_2, distance, # of observation in the new cluster]
        #linkage_matrix.append([a_idx, b_idx, dist, len(c['n_idx'])])
        linkage_matrix.append([a_idx, b_idx, float(len(c['n_idx'])), len(c['n_idx'])])
            
    return clusters, np.array(linkage_matrix)


def match_indexes(indexes, query_str, portion_min_length = 15): # video_length is in secs
    '''
    Return a list of tuples (video_name, best_node, score)
    '''
    
    matched_nodes = []    

    for video_name in indexes:
        best_node, score = match_index(indexes[video_name], query_str, portion_min_length)
        matched_nodes += [(video_name, best_node, score)]
    
    return matched_nodes


def match_index(clusters, query_str, portion_min_length = 15): # video_length is in secs
    
    query_tf = {}
    for w in query_str.split(' '):
        if w not in query_tf:
            query_tf[w] = 1
        else:
            query_tf[w] += 1

    # 
    portion_min_length = min(portion_min_length * 30, max(clusters[-1]['n_idx']) - min(clusters[-1]['n_idx']))  


    dfs_dists = [] 
    # DFS    
    cur_node = clusters[-1]
    dfs_dists += [1-getCosSimilarty(query_tf, cur_node['tf'])]
    while (len(cur_node['descs']) > 0) or (max(cur_node['n_idx']) - min(cur_node['n_idx']) > portion_min_length):

        a_node = clusters[cur_node['descs'][0]]
        b_node = clusters[cur_node['descs'][1]]

        a_sim = getCosSimilarty(query_tf, a_node['tf'])
        b_sim = getCosSimilarty(query_tf, b_node['tf'])

        b_length = max(b_node['n_idx']) - min(b_node['n_idx'])
        a_length = max(a_node['n_idx']) - min(a_node['n_idx'])

        max_sim = max(a_sim, b_sim)
        dfs_dists += [1-max_sim]
    
          
        node = b_node
        length = b_length
        if a_sim > b_sim:
            node = a_node
            length = a_length
        
        if length < portion_min_length:
            break

        cur_node = node

    return cur_node, getCosSimilarty(query_tf, cur_node['tf'])

def plot_cluster(clusters, linkage_matrix):
    
    ax = dendrogram(linkage_matrix, count_sort='ascending', leaf_rotation= 90)
    plt.show()

def store_cluster(clusters, linkage_matrix, video_name):

    for node in clusters:
        print node      


