import numpy as np
from .LocalPosterior import LocalPrior, LocalLikelihood

def Prior(dag):
    '''a function computing graph global prior: p(G) '''
    '''
    parameters:
    -----------
    dag: the global structure 
    prior: graph prior p(G)
    '''
    N = np.shape(dag)[0]
    prior = 1
    for i in range(N):
        ind = np.argwhere(dag[:, i] == 1).reshape(-1,)
        prior *= LocalPrior(i, ind, N)
    return prior

def LogLikelihood(data, dag, node_sizes, alpha):
    '''a function of computing graph log likelihood: p(D|G)'''
    '''
    parameters:
    -----------
    data: input data
    dag: input graph
    node_sizes: the number of states for each variable
    alpha: pseudo_count 
    LL: log likelihood of G
    '''
    LL = 0
    N = np.shape(dag)[0]
    for i in range(N):
        ind = np.argwhere(dag[:,i] == 1).reshape(-1,)
        l,ll = LocalLikelihood(i, ind, data, node_sizes, alpha)
        LL += ll
    return LL

def Posterior(data, dag, node_sizes, alpha):
    '''a function of computing graph posterior probability: p(G|D)'''
    '''
    parameters:
    -----------
    data: input data
    dag: input graph
    node_sizes: the number of states for each variable
    alpha: pseudo_count 
    P: Posterior probability of G
    '''
    prior = Prior(dag)
    LL = LogLikelihood(data, dag, node_sizes, alpha)
    P = np.exp(LL) * prior
    return P