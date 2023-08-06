import numpy as np 
import pandas as pd 
import graphviz
import pydot
from pycausal.pycausal import pycausal as pc 
from pycausal import search as s 
import lingam
from lingam.utils import make_dot
import pickle
import scipy.io as sio
# import igraph as ig 
from sklearn.preprocessing import KBinsDiscretizer
from sklearn.linear_model import LinearRegression
from pgmpy.base import  DAG
from pgmpy.models import BayesianModel 
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.inference import VariableElimination
from sklearn.metrics import f1_score, accuracy_score

class Model():
	def __init__(self, 
				 method = "LiNGAM-ICA", 
				 estimator = "Linear Gaussian",
				 W = None,
				 residual = None,
				 variable_names = None):
		self.W = W
		self.method = method # the method is "LiNGAM-ICA", "LiNGAM-Direct"
		self.variable_names = variable_names
		self.estimator = estimator # default as "Linear Gaussian" 
		self.residual = residual

	def fit(self, 
			X_train, 
			y_train, 
			verbose = False):
		"""
		Input: 
		X_train: Attributes of training data, in the format of np.DataFrame, size n*(d-1) with variable names as columns
		y_train: Labels of training data, in the format of np.DataFrame, size n*1 with variable name as column

		"""
		# self.variable_names = X_train.columns.to_list() + y_train.columns.to_list()

		# Perform continuous structure learning
		train_data = pd.DataFrame(np.concatenate((X_train, y_train.reshape(-1,1)), axis = 1), columns = self.variable_names)
		if self.method == "LiNGAM-ICA":
			model = lingam.ICALiNGAM(max_iter=5000)
		elif self.method == "LiNGAM-Direct":
			model = lingam.DirectLiNGAM()
		model.fit(train_data)
		self.W = model.adjacency_matrix_

		# Linear Gaussian to estimate residual of target variable
		residual = np.mean(y_train.reshape(-1,) - np.dot(X_train , self.W[-1,:-1].reshape(-1,)))
		self.residual = residual
		

	def predict(self, X_test):
		"""
		Input:
		X_test: Attributes of testing data, in the format of np.DataFrame, size n*(d-1) with variable names as columns

		Output:
		y_pred: prediction of testing data labels, in the format of np.DataFrame, size n*1 with variable name as column

		"""
		y_pred = np.dot(X_test , self.W[-1,:-1].reshape(-1,)) + self.residual
		return y_pred

	
