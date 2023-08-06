import numpy as np
import copy
from .util import h_dag

def CandidateDAGs(dag):
    ''' a function to heurstic search the neighboring dags '''
    '''
    parameters:
    -----------
    dag: the dag of current state, a N*N numpy array
    dags_f: the set of neighboring dags: a dictionary of N*N numpy array
    '''

    dags = dict()
    N = np.shape(dag)[0]

    for i in range(N): # enumerate X1, X2, ...XN
        # Remove a link for Xi
        ind = np.argwhere(dag[i, :] == 1).reshape(-1,)
        for ii in range(len(ind)):
            dag_new = copy.deepcopy(dag)
            dag_new[i, ind[ii]] = 0
            dags[len(dags)] = dag_new
            del dag_new

        # Reverse a link for Xi
        for ii in range(len(ind)):
            dag_new = copy.deepcopy(dag)
            dag_new[i, ind[ii]] = 0
            dag_new[ind[ii], i] = 1
            dags[len(dags)] = dag_new
            del dag_new

        # Add a link for Xi
        ind_0 = np.argwhere(dag[i, :] == 0).reshape(-1,)
        if i in ind_0:
            ind_0 = ind_0[ind_0 != i]
        for ii in range(len(ind_0)):
            dag_new = copy.deepcopy(dag)
            dag_new[i, ind_0] = 1
            dags[len(dags)] = dag_new
            del dag_new

    # Use NOTEARS DAG constraint check whether the obtained graph is DAG or not
    dags_f = dict()
    for iii in range(len(dags)):
        dag = dags[iii]
        h = h_dag(dag, N)
        if h == 0:
            dags_f[len(dags_f)] = dag
        del dag

    return dags_f



