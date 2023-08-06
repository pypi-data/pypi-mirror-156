import numpy as np
from scipy.special import comb
from .util import bdeu



def LocalPrior(node, ps, d):
    '''a function computing local prior: p(Gi) = 1 / comb(d-1, |pa(x_i)|)'''
    '''
    parameters:
    -----------
    node: i, index of Xi
    ps: indices of parent variable of variable Xi
    d: dimension, total number of variables
    p: local graph prior p(Gi)
    '''
    n_ps = len(ps)
    p = 1 / comb(d-1, n_ps)
    return p

def LocalLikelihood(node, ps, data, node_sizes, alpha):
    '''a function to compute the local log likelihood: p(D|Gi)'''
    '''
    parameters:
    -----------
    node: i, index of Xi
    ps: indices of parent variable of variable Xi
    d: dimension, total number of variables
    data: input data M sample N variables ndarray of M*N
    node_sizes: the number of states for each variable
    alpha: pseudo_count 
    ll: log likelihood
    l: likelihood 
    '''
    if len(ps) == 0: # no parent case
        count = np.zeros((node_sizes[node],1))
        for s in range(node_sizes[node]):
            count[s,0] = len(np.argwhere(data[:,node] == s).reshape(-1,))
    else:
        n_ps = len(ps) # number of parent variables
        a = list() # list a to store the possible states for all parent variables
        for i in range(n_ps):
            a.append(list(np.arange(node_sizes[ps[i]])))
        ps_comb = [list(x) for x in np.array(np.meshgrid(*a)).T.reshape(-1, len(a))] # ps_comb store all the possible parent configurations
        ps_comb = np.array(ps_comb)
        n_ps_comb = len(ps_comb) # number of parent configuration
        count = np.zeros((node_sizes[node], n_ps_comb))
        for j in range(n_ps_comb):
            p_config = ps_comb[j,:] # parent configuration
            ind = np.argwhere(np.sum(data[:, ps] == p_config,axis = 1) == n_ps).reshape(-1,)
            data_c = data[ind,:] # find all the samples with the specified parent configuration
            for s in range(node_sizes[node]):
                ind_s = np.argwhere(data_c[:, node] == s).reshape(-1,)
                count[s,j] = len(ind_s)
    # compute likelihood
    ll = bdeu(count,alpha)
    l = np.exp(ll)
    return l,ll

def LocalPosterior(node, ps, data, node_sizes, alpha):
    ''' a function of computing the posterior probability'''
    '''
    -----------
    node: i, index of Xi
    ps: indices of parent variable of variable Xi
    data: input data M sample N variables ndarray of M*N
    d: dimension, total number of variables
    node_sizes: the number of states for each variable
    alpha: pseudo_count 
    p: posterior probability p(Gi|D) propto p(D|Gi)p(Gi)
    '''
    d = np.shape(data)[1]
    prior = LocalPrior(node, ps, d)
    l,_ = LocalLikelihood(node, ps, data, node_sizes,alpha)
    p = prior * l
    return p, l, prior
