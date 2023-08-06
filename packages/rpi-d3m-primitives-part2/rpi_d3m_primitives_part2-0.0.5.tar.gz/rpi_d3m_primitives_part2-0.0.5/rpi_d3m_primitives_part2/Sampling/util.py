# -*- coding: utf-8 -*-
# author: Hanjing Wang

import numpy as np
from sklearn import linear_model
from scipy.special import gammaln
def h_dag(W,d):
    """Evaluate value and gradient of acyclicity constraint."""
    '''
    W: weighted adjacency matrix
    d: number of nodes
    '''
    #     E = slin.expm(W * W)  # (Zheng et al. 2018)
    #     h = np.trace(E) - d
    M = np.eye(d) + W * W / d  # (Yu et al. 2019)
    E = np.linalg.matrix_power(M, d - 1)
    h = (E.T * M).sum() - d
    # G_h = E.T * W * 2
    # return h,G_h
    return h

def linear_regression(data,child, parent,intercept):
    '''
    Parameters
    ----------
    data : N by d np.array
    child : a list of one number,i.e. [0]
    parent : a list of numbers, i.e. [1,2], []
    intercept : True or False (to decide whether to include the intercept during regression)
    Returns
    -------
    lm : a linear regression model in sklearn
    error : mean square error
    '''
    X = data[:,parent]
    y = data[:,child]
    lm = linear_model.LinearRegression(fit_intercept = intercept)
    model = lm.fit(X,y)
    predictions = lm.predict(X)
    error = np.sum(np.square(predictions-y))
    return lm,error

def bic_c(data,child, parent,intercept):
    '''a function that output the local BIC score for linear Gaussian data'''
    '''
    Parameters
    ----------
    data : N by d np.array
    child : a list of one number,i.e. [0]
    parent : a list of numbers, i.e. [1,2], []
    intercept : True or False (to decide whether to include the intercept during regression)
    Returns
    -------
    bic: the local bic score for node[child] with parents node[parents]
    '''  
    n=len(data)
    length = len(parent)
    if length>=1:
        error = linear_regression(data,child, parent,intercept)[1]
        sigma_square = error/n
        log_like= -0.5*(1/sigma_square)*error - 0.5*n*np.log(2*np.pi*sigma_square)
        bic = log_like - 0.5*(length+1)*np.log(n)
        return bic
    else:
        y = data[:,child]
        mean = np.mean(y)
        error = np.sum(np.square(y-mean))
        sigma_square = error/n
        log_like= -0.5*(1/sigma_square)*error - 0.5*n*np.log(2*np.pi*sigma_square)
        bic = log_like - 0.5*np.log(n)
        return bic
def get_bic_score(data,adjacency,intercept):
    '''a function that compute the BIC score for a BN given structure'''
    '''
    Parameters
    ----------
    data : N by d np.array
    adjacency: the binary adjacency matrix 
                the adjacency matrix (i,j) represent that there is a link from node j to node i
    intercept : True or False (to decide whether to include the intercept during regression)
    Returns
    -------
    score: the bic score for for the whole structure
    parameter: the corresponding weighted adjacency matrix for the Linear Gaussian BN
    '''  
    # here 
    d = len(adjacency)
    score = 0
    parameter = np.zeros((d,d))
    for i in range(d):
        child = [i]
        parents = np.where(adjacency[i,:]==1)[0]
        if len(parents)>=1:
            lm,_ = linear_regression(data,child, parents,intercept)
            parameter_i = lm.coef_
            parameter[child,parents] = parameter_i
        score_i = bic_c(data,child,parents,intercept)
        score = score + score_i
    return score,parameter

def bdeu(count_ijk,alpha):
    '''a function that compute the local BDEU score for a BN given structure'''
    '''
    Parameters
    ----------
    count_ijk: a count matrix, count_ijk[m,n] represent count(X_i=m,pi(X_i)=n)
    alpha: the equivalent sample size
    Returns
    -------
    the local BDEU score for node i 
    '''  
    count_ij = np.sum(count_ijk,axis=0)
    alpha_ijk = np.zeros(count_ijk.shape)+alpha/count_ijk.size
    alpha_ij = np.zeros(count_ij.shape)+alpha/count_ij.size
    temp_ijk = gammaln(count_ijk+alpha_ijk)-gammaln(alpha_ijk)
    temp_ij = gammaln(alpha_ij)-gammaln(alpha_ij+count_ij)
    return np.sum(temp_ijk)+np.sum(temp_ij)
