import numpy as np
import pandas as pd
import scipy.io as sio
# import igraph as ig
from sklearn.preprocessing import KBinsDiscretizer
from pgmpy.base import  DAG
from pgmpy.models import BayesianModel
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.inference import VariableElimination
from rpi_d3m_primitives_part2.Sampling.MetropolisHastingSampler import MultiChainMetropolisHastingSampler as MCMHSampler

class BayesianClassifier():
    def __init__(self,
                DAG = None,
                S = 5,
                L = 5,
                burnin = 100,
                random_seed = 0,
                equivalent_sample_size = 1):
        self.DAG = DAG
        self.L = L
        self.S = S
        self.burnin = burnin
        self.equivalent_sample_size = equivalent_sample_size
        self.random_seed = random_seed

    def fit(self,
            X_train,
            y_train,
            variable_names,
            state_names,
            stateNO,
            seeddag,
            verbose = False):
        # self.variable_names = X_train.columns.to_list() + y_train.columns.to_list()
        self.variable_names = variable_names
        self.state_names = state_names
        self.stateNO = stateNO

        d = len(self.variable_names)
        self.d = d
        # seeddag = np.zeros((d,d))
        train_data = np.concatenate((X_train, y_train.reshape(-1,1)), axis = 1)
        # self.train_data = train_data
        dags = MCMHSampler(train_data, self.stateNO, self.burnin, self.L, self.S, seeddag, self.random_seed, self.equivalent_sample_size)

        DAGs = np.zeros((self.S,d,d))
        for s in range(self.S):
            DAGs[s,:,:] = dags[s]
        self.DAG = DAGs
        return DAGs


    def predict(self,
                X_test,
                train_data,
                # variable_names,
                stateNO,
                statenames):
        M = np.shape(X_test)[0]
        d = np.shape(train_data)[1]
        prob = np.zeros((M, stateNO[-1]))
        train_data = pd.DataFrame(train_data)
        variable_names = [str(x) for x in train_data.columns.to_list()]
        train_data.columns = variable_names
        for s in range(self.S):
            # build a BN object
            BN = BayesianModel()
            BN.add_nodes_from(nodes = variable_names)

            # input the DAG
            dag = self.DAG[s,:,:]
            for p in range(d):
                for c in range(d):
                    if dag[p,c] == 1:
                        BN.add_edge(variable_names[p], variable_names[c])

            # parameter learning
            BN.fit(train_data,
                   estimator = BayesianEstimator,
                   state_names = statenames,
                   prior_type= 'BDeu',
                   equivalent_sample_size =  self.equivalent_sample_size)

            # inference
            X_test = pd.DataFrame(X_test, columns = variable_names[:-1])
            prob += BN.predict_probability(X_test).values

        # find the state with maximum probability
        Y_est = np.argmax(prob, axis = 1)
        # Y_est = pd.DataFrame(Y_est, columns=[variable_names[-1]])
        return Y_est
