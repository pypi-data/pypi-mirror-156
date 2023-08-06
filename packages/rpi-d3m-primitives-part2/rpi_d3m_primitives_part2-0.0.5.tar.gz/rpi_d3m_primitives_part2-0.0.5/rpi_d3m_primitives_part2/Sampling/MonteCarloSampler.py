import numpy as np

def MonteCarloSampler(p):
    ''' a function to sample using Monte Carlo Sampling Method '''
    '''
    parameters:
    -----------
    p: a numpy array of size 1*N includes the probability for all states
    v: the index of the sampled state
    '''
    p = np.reshape(p, [-1,])
    n = len(p)
    u = np.random.rand(1)
    if u < p[0]:
        v = 0
    else:
        for i in range(1,n):
            if u <= np.sum(p[:i+1]) and u > np.sum(p[:i]):
                v = i
    return v


