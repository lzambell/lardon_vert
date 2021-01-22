import config as cf
import data_containers as dc

import numpy as np
import sklearn.cluster as skc
import scipy.spatial as spatial
import scipy.sparse.csgraph as csgr


def dbscan(eps, min_samp, y_squeez):    


    for iview in range(cf.n_View):

        """try to cluster un-clustered hits only"""
        hits = [x for x in dc.hits_list if x.view==iview and x.cluster == -1]
        if(len(hits)==0): continue

        """ squeeze y axis instead of rebinning or defining a new metric """
        #data = [[x.channel,x.max_t*y_squeez] for x in hits]
        data = [[x.X,x.Z*y_squeez] for x in hits]
        X = np.asarray(data)
        db = skc.DBSCAN(eps=eps,min_samples=min_samp).fit(X)
        labels = db.labels_

        for h,cluster in zip(hits, labels):
            h.cluster = cluster if cluster==-1 else cluster + dc.evt_list[-1].nClusters[iview]

        n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
        dc.evt_list[-1].nClusters[iview] += n_clusters
    


def mst(r_max, n_min):


    for iview in range(cf.n_View):

        """try to cluster un-clustered hits only"""
        hits = [x for x in dc.hits_list if x.view==iview and x.cluster == -1]
        if(len(hits) < n_min): continue
        coord = np.asarray([(x.X, x.Z) for x in hits])

        """ compute the distance between each points"""
        graph = spatial.distance.cdist(coord, coord, 'euclidean')
        """ keep only the two closest points """
        #graph = graph * (graph < np.sort(graph, axis=-1)[:,[n_NN]])
        """ keep only short edges """
        graph[graph > r_max] = 0.
            
        """ compute the MST from this graph """
        T = csgr.minimum_spanning_tree(csgraph=graph)
        n_components, labels = csgr.connected_components(csgraph=T, directed=False, return_labels=True)

        n_clusters = 0
        for n in range(n_components):
            idx = np.where(labels==n)[0]
            if(len(idx) <= n_min):
                continue
            else: 
                for i in idx:                        
                    hits[i].cluster = n_clusters
                n_clusters += 1
        dc.evt_list[-1].nClusters[iview] = n_clusters

                
                
