import numpy as np
from .CandidateDAGs import CandidateDAGs
from .MonteCarloSampler import MonteCarloSampler as MCSampler
from .Posterior import Prior
from .Posterior import LogLikelihood as LL


def MetropolisHastingSampler(data, node_sizes, burnin, S, seeddag, random_seed, alpha):

    # initial state
    dag = seeddag
    N = np.shape(dag)[0]
    np.random.RandomState(seed=int(random_seed))
    # begin burnin period
    t = 0
    for t in range(burnin):
        # heurstic search for neighbor dags
        dags_new_step = CandidateDAGs(dag)
        p = np.ones([1, len(dags_new_step)]) / len(dags_new_step)
        dag_new = dags_new_step[MCSampler(p)]

        # compute acceptance
        r = np.exp(LL(data, dag_new, node_sizes, alpha) - LL(data, dag, node_sizes, alpha)) * Prior(dag_new) * len(dags_new_step) / (Prior(dag) * len(CandidateDAGs(dag_new)))
        a = min(1,r)
        u = np.random.rand(1)
        if u <= a:
            dag = dag_new
            del dag_new

    print("Burinin finished!\n")

    dags = dict()
    t = 1

    while(len(dags) < S):
        # heurstic search for neighbor dags
        dags_new_step = CandidateDAGs(dag)
        p = np.ones([1, len(dags_new_step)]) / len(dags_new_step)
        dag_new = dags_new_step[MCSampler(p)]

        # compute acceptance
        r = np.exp(LL(data, dag_new, node_sizes, alpha) - LL(data, dag, node_sizes, alpha)) * Prior(dag_new) * len(
            dags_new_step) / (Prior(dag_new) * len(CandidateDAGs(dag_new)))
        a = min(1, r)
        u = np.random.rand(1)
        if u <= a:
            dag = dag_new
            del dag_new
            if t%10 == 0:
                dags[len(dags)] = dag
        t += 1

    return dags

def dag_next(data, dag, node_sizes, alpha):
    # heurstic search for neighbor dags
    dags_new_step = CandidateDAGs(dag)
    p = np.ones([1, len(dags_new_step)]) / len(dags_new_step)
    dag_new = dags_new_step[MCSampler(p)]

    # compute acceptance
    r = np.exp(LL(data, dag_new, node_sizes, alpha) - LL(data, dag, node_sizes, alpha)) * Prior(dag_new) * len(
        dags_new_step) / (Prior(dag) * len(CandidateDAGs(dag_new)))
    a = min(1, r)
    u = np.random.rand(1)
    if u <= a:
        dag = dag_new
    # if accept -> dag_new; otherwise dag
    return dag

def MultiChainMetropolisHastingSampler(data, node_sizes, burnin, L, S, seeddag, random_seed, alpha):

    # initial state
    dag = seeddag
    N = np.shape(dag)[0]
    np.random.RandomState(seed=int(random_seed))
    dags_all_chain = dict()
    for l in range(L):
        dags_all_chain[l] = dag
    # begin burnin period
    t = 0
    for t in range(burnin):
        # print(t)
        for l in range(L):
            dags_all_chain[l] = dag_next(data, dags_all_chain[l], node_sizes, alpha)

    print("Burinin finished!\n")

    dags = dict()
    t = 1
    while(len(dags) < S):
        # print(len(dags))
        for l in range(L):
            dag = dags_all_chain[l]
            # heurstic search for neighbor dags
            dags_new_step = CandidateDAGs(dag)
            p = np.ones([1, len(dags_new_step)]) / len(dags_new_step)
            dag_new = dags_new_step[MCSampler(p)]

            # compute acceptance
            r = np.exp(LL(data, dag_new, node_sizes, alpha) - LL(data, dag, node_sizes, alpha)) * Prior(dag_new) * len(dags_new_step) / (Prior(dag_new) * len(CandidateDAGs(dag_new)))
            a = min(1, r)
            u = np.random.rand(1)
            if u <= a:
                dag = dag_new
                dags_all_chain[l] = dag_new
                del dag_new
                if t%10 == 0:
                    dags[len(dags)] = dag
            del dag
        t += 1

    return dags