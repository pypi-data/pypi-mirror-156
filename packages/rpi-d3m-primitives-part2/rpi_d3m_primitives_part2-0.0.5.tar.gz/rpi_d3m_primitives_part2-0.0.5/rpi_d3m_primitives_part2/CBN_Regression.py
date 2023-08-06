import os, sys
import typing
import scipy.io
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.impute import SimpleImputer
from collections import OrderedDict
from typing import cast, Any, Dict, List, Union, Sequence, Optional, Tuple
from d3m import container, utils
from d3m.metadata import base as metadata_base
from d3m.metadata import hyperparams
from d3m.metadata import params
from d3m.primitive_interfaces.supervised_learning import SupervisedLearnerPrimitiveBase
from d3m.primitive_interfaces import base
from d3m.primitive_interfaces.base import CallResult
import rpi_d3m_primitives_part2
from rpi_d3m_primitives_part2.structuredClassifier.ContinuousBN_Regressor_model import Model
from sklearn.impute import SimpleImputer
from rpi_d3m_primitives_part2.featSelect.RelationSet import RelationSet
import graphviz
from graphviz import Digraph
import lingam
from lingam.utils import make_dot
import pydot


Inputs = container.DataFrame
DAG = container.ndarray
Outputs = container.DataFrame

__all__ = ('CBN_Regression',)

class Params(params.Params):
    strategy_: Optional[str]
    method_: Optional[str]
    origin_inputs_: Optional[pd.DataFrame] # potential problem of using 'pd.DataFrame'
    origin_outputs_: Optional[pd.DataFrame] # potential problem of using 'pd.DataFrame'
    train_data_: Optional[Union[np.ndarray, List[np.ndarray]]]
    train_label_: Optional[Union[np.ndarray, List[np.ndarray]]]
    target_columns_metadata_: Optional[List[OrderedDict]]
    structure_: Optional[Union[np.ndarray, List[np.ndarray]]]
    residual_: Optional[float]
    dimension_: Optional[int]
    structure_fit_: Optional[bool]

    
class Hyperparams(hyperparams.Hyperparams):
    strategy = hyperparams.Enumeration[str](
            values=['mean', 'most_frequent', 'median'],
            default='most_frequent',
            description='The method for imputer.',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter']
            )
    method = hyperparams.Enumeration[str](
            values=['LiNGAM-ICA', 'LiNGAM-Direct'],
            default='LiNGAM-ICA',
            description='The method for continuous Causal Discovery.',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/TuningParameter']
            )

class CBN_Regression(SupervisedLearnerPrimitiveBase[Inputs, Outputs, Params, Hyperparams]):
    """
     A primitive which does global causal discovery. It reveals the causal relations between features which encoded in the given data. To demonstrate its application, the algorithm also implement a Bayesian Network Regressor use the results of the global causal discovery.
    """
    __git_commit__ = utils.current_git_commit(os.path.dirname(__file__))
    metadata = metadata_base.PrimitiveMetadata({
        'id': '05dce570-ce88-45f6-a270-72dd10bc001c',
        'version': rpi_d3m_primitives_part2.__coreversion__,
        'name': 'Global Causal Discovery',
        'keywords': ['Global Causal Discovery','Causal Graphical Graph','Regression'],
        'description': 'This algorithm is an implementation of widely used global causal discovery. It reveals the causal relations between features which encoded in the given data. To demonstrate its application, the algorithm also implement a Bayesian Network Regressor use the results of the global causal discovery. ',
        'source': {
            'name': rpi_d3m_primitives_part2.__author__,
            'contact': 'mailto:yinn2@rpi.edu',
            'uris': [
                'https://gitlab.com/N.Yin/rpi-d3m-part2/-/blob/{git_commit}/rpi_d3m_primitives_part2/CBN_Regression.py'.format(
                    git_commit = __git_commit__),
                # 'https://gitlab.com/N.Yin/rpi-d3m-part2/-/blob/master/rpi_d3m_primitives_part2/GCD_Classification.py',
                'https://gitlab.com/N.Yin/rpi-d3m-part2.git'
                ]
        },
        'installation':[{
            'type' : metadata_base.PrimitiveInstallationType.UBUNTU,
            'package': 'openjdk-8-jdk-headless',
            'version': '8u252-b09-1~18.04'

        }, 
        {
            'type': metadata_base.PrimitiveInstallationType.UBUNTU,
            'package': 'graphviz',
            'version': '2.40.1-2'

        }, 
        # {
        #     'type': metadata_base.PrimitiveInstallationType.PIP,
        #     'package_uri':'git+https://github.com/bd2kccd/py-causal.git@{git_commit}#egg={egg}'.format(
        #         git_commit='6201db7d21aa453a8b66bf632db930417209a430', egg='pycausal')

        # }, 
        {
            'type': metadata_base.PrimitiveInstallationType.PIP,
            'package_uri':'git+https://gitlab.com/N.Yin/rpi-d3m-part2.git@{git_commit}#egg={egg}'.format(
                git_commit=__git_commit__, egg='rpi_d3m_primitives_part2')
            # 'package': 'rpi_d3m_primitives_part2',
            # 'version': rpi_d3m_primitives_part2.__version__
        }],
        'python_path': 'd3m.primitives.regression.global_causal_discovery.RegressorRPI',
        'algorithm_types': [
            metadata_base.PrimitiveAlgorithmType.MULTIVARIATE_REGRESSION],
        'primitive_family': metadata_base.PrimitiveFamily.REGRESSION
    })


    def __init__(self, *, hyperparams: Hyperparams, random_seed: int = 0, docker_containers: typing.Union[typing.Dict[str, base.DockerContainer]] = None) -> None:
        super().__init__(hyperparams=hyperparams, random_seed=random_seed, docker_containers=docker_containers)
        # parameters
        self._index = None
        self._fitted = False
        # hyperparameters
        self._strategy = self.hyperparams['strategy']
        self._method = self.hyperparams['method']
        # Other parameters
        self._training_inputs = None
        self._training_outputs = None
        self._origin_inputs = None #for label encoder
        self._origin_outputs = None # for label encoder
        # self._cate_flag = None
        self._LEoutput = LabelEncoder() #label encoder
        self._Imputer = SimpleImputer(missing_values=np.nan, strategy=self._strategy) #imputer
        self._scaler = MinMaxScaler() 
        # self._Kbins = KBinsDiscretizer(n_bins=self._nbins, encode='ordinal', strategy=self._strategy) #KbinsDiscretizer
        # self._discTrainset = None
        self._target_columns_metadata = None
        self._structure = None
        self._residual = None
        self._structure_fit = False
        self._dimension = None 
        self._names = None # variable names
        
    
    def _store_target_columns_metadata(self, outputs: Outputs) -> None:
        outputs_length = outputs.metadata.query((metadata_base.ALL_ELEMENTS,))['dimension']['length']

        target_columns_metadata: List[Dict] = []

        for column_index in range(outputs_length):
            column_metadata = OrderedDict(outputs.metadata.query_column(column_index))

            # Update semantic types and prepare it for predicted targets.
            semantic_types = list(column_metadata.get('semantic_types', []))
            if 'https://metadata.datadrivendiscovery.org/types/PredictedTarget' not in semantic_types:
                semantic_types.append('https://metadata.datadrivendiscovery.org/types/PredictedTarget')
            semantic_types = [semantic_type for semantic_type in semantic_types if semantic_type != 'https://metadata.datadrivendiscovery.org/types/TrueTarget']
            column_metadata['semantic_types'] = semantic_types

            target_columns_metadata.append(column_metadata)
            
        self._target_columns_metadata = target_columns_metadata
        

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:

        ## Update semantic types and prepare it for predicted targets
        self._store_target_columns_metadata(outputs)
        
        ## memory original training inputs
        self._origin_inputs = inputs
        self._origin_outputs = outputs

        feature_names = inputs.columns.to_list()+outputs.columns.to_list()
        self._names = []

        ## set training labels
        metadata = outputs.metadata
        column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, 0))
        semantic_types = column_metadata.get('semantic_types', [])
        # if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
        #     self._LEoutput.fit(outputs)
        #     self._training_outputs = self._LEoutput.transform(outputs) #starting from zero
        # else:
        self._training_outputs = outputs.astype('float64').values
        
        
        ## convert categorical values to numerical values in training data
        metadata = inputs.metadata
        [m,n] = inputs.shape
        self._training_inputs = np.zeros((m,n))
        self._cate_flag = np.zeros((n,))
        for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
            if column_index is metadata_base.ALL_ELEMENTS: 
                continue
            column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
            semantic_types = list(column_metadata.get('semantic_types', []))
            if 'https://metadata.datadrivendiscovery.org/types/Attribute' in semantic_types and len(semantic_types) == 1:
                semantic_types.append('https://metadata.datadrivendiscovery.org/types/Float')

            try:
                inputs.iloc[:, column_index] = inputs.iloc[:, column_index].astype('float64')
                temp = list(inputs.iloc[:, column_index].values)
                for i in np.arange(len(temp)):
                    if bool(temp[i]):
                        self._training_inputs[i,column_index] = float(temp[i])
                    else:
                        self._training_inputs[i,column_index] = float('nan')
                # imputer will remove the column with purely missing values
                if not np.count_nonzero(np.isnan(self._training_inputs[:, column_index])) == 0:  # if there is missing values
                    if np.count_nonzero(np.isnan(self._training_inputs[:, column_index])) == m:  # all missing
                        self._training_inputs[:, column_index] = np.zeros(m, )  # replace with all zeros
                self._names.append(feature_names[column_index])
            except:
                if 'http://schema.org/Text' in semantic_types:
                    pass
                else:
                    LE = LabelEncoder()
                    LE = LE.fit(inputs.iloc[:,column_index])
                    self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])
                    # self._cate_flag[column_index] = 1
                    self._names.append(feature_names[column_index])

            # if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
            #     LE = LabelEncoder()
            #     LE = LE.fit(inputs.iloc[:,column_index])
            #     self._training_inputs[:,column_index] = LE.transform(inputs.iloc[:,column_index])
            #     self._cate_flag[column_index] = 1
            #     self._names.append(feature_names[column_index])
            # elif 'http://schema.org/Text' in semantic_types:
            #     pass
            # else:
            #     temp = list(inputs.iloc[:, column_index].values)
            #     for i in np.arange(len(temp)):
            #         if bool(temp[i]):
            #             self._training_inputs[i,column_index] = float(temp[i])
            #         else:
            #             self._training_inputs[i,column_index] = float('nan')
            #     # imputer will remove the column with purely missing values
            #     if not np.count_nonzero(np.isnan(self._training_inputs[:, column_index])) == 0:  # if there is missing values
            #         if np.count_nonzero(np.isnan(self._training_inputs[:, column_index])) == m:  # all missing
            #             self._training_inputs[:, column_index] = np.zeros(m, )  # replace with all zeros
            #     self._names.append(feature_names[column_index])

        self._names.append(feature_names[-1])
        self._fitted = False
    

    def fit(self, *, timeout: float = None, iterations: int = None) -> None:
        if self._fitted:
            return CallResult(None)

        if self._training_inputs.any() == None or self._training_outputs.any() == None: 
            raise ValueError('Missing training data, or missing values exist.')

        X_train = np.zeros(list(np.shape(self._training_inputs))) # nsamples * d-1
        y_train = self._training_outputs # nsamples * 1

        ## impute missing values and scale 
        for i in range(self._training_inputs.shape[1]):
            self._Imputer.fit(self._training_inputs[:, i:i+1])
            X_train[:, i:i+1] = self._Imputer.transform(self._training_inputs[:, i:i+1])
            self._scaler.fit(X_train[:, i:i+1])
            X_train[:, i:i+1] = self._scaler.transform(X_train[:, i:i+1])

        ## fit the regressor
        clf = Model(method = self._method, variable_names = self._names)
        clf.fit(X_train, y_train)
        self._structure = clf.W 
        self._residual = clf.residual
        self._structure_fit = True
        self._fitted = True

        np.savetxt('Causal_Structure.txt', self._structure.T, delimiter = ',')
        g = Digraph(format = 'png')
        g = make_dot(self._structure.T, labels = self._names)
        g.render('Causal_Graph', view = False, cleanup = True)

        return CallResult(None)


    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> base.CallResult[Outputs]:  # inputs: m x n numpy array
        if self._fitted:

            # put a placehold of training and inputs data so that it does not change
            training_inputs = self._training_inputs
            training_outputs = self._training_outputs

            # Data processing the test data: convert categorical values to numerical values in testing data
            metadata = inputs.metadata
            [m, n] = inputs.shape
            X_test = np.zeros((m, n))
            for column_index in metadata.get_elements((metadata_base.ALL_ELEMENTS,)):
                # print(column_index)
                if column_index is metadata_base.ALL_ELEMENTS:
                    continue
                column_metadata = metadata.query((metadata_base.ALL_ELEMENTS, column_index))
                semantic_types = list(column_metadata.get('semantic_types', []))
                if 'https://metadata.datadrivendiscovery.org/types/Attribute' in semantic_types and len(semantic_types) == 1:
                    semantic_types.append('https://metadata.datadrivendiscovery.org/types/Float')

                try:
                    # if the semantic type is integer or float
                    inputs.iloc[:, column_index] = inputs.iloc[:, column_index].astype('float64')
                    temp = list(inputs.iloc[:, column_index].values)
                    for i in np.arange(len(temp)):
                        if bool(temp[i]):
                            X_test[i, column_index] = float(temp[i])
                        else:
                            X_test[i, column_index] = float('nan')
                except:
                    if 'http://schema.org/Text' in semantic_types:
                        pass
                    else:
                        # if the semantic type is categorical data
                        LE = LabelEncoder()
                        LE = LE.fit(self._origin_inputs.iloc[:, column_index]) #use training data to fit
                        X_test[:, column_index] = LE.transform(inputs.iloc[:, column_index])

                # if 'https://metadata.datadrivendiscovery.org/types/Attribute' in semantic_types and len(semantic_types) == 1:
                #     semantic_types.append('https://metadata.datadrivendiscovery.org/types/CategoricalData')
                # if 'https://metadata.datadrivendiscovery.org/types/CategoricalData' in semantic_types:
                #     LE = LabelEncoder()
                #     LE = LE.fit(self._origin_inputs.iloc[:, column_index]) #use training data to fit
                #     # print(column_index)
                #     X_test[:, column_index] = LE.transform(inputs.iloc[:, column_index])
                # elif 'http://schema.org/Text' in semantic_types:
                #     pass
                # else:
                #     temp = list(inputs.iloc[:, column_index].values)
                #     for i in np.arange(len(temp)):
                #         if bool(temp[i]):
                #             X_test[i, column_index] = float(temp[i])
                #         else:
                #             X_test[i, column_index] = float('nan')

            ## impute missing values and scale 
            for i in range(training_inputs.shape[1]):
                self._Imputer.fit(training_inputs[:, i:i+1])
                training_inputs[:,i:i+1] = self._Imputer.transform(training_inputs[:,i:i+1])
                X_test[:, i:i+1] = self._Imputer.transform(X_test[:, i:i+1])
                self._scaler.fit(training_inputs[:, i:i+1])
                X_test[:, i:i+1] = self._scaler.transform(X_test[:, i:i+1])

            ## prediction
            clf = Model(W = self._structure, residual = self._residual, method = self._method, variable_names = self._names)
            output = clf.predict(X_test)

            ## label decode
            # self._LEoutput.fit(self._origin_outputs)
            # output = self._LEoutput.inverse_transform(output.reshape((-1,)).astype('int64'))
            
            ## update metadata
            output = container.DataFrame(output, generate_metadata=False, source=self)
            output.metadata = inputs.metadata.clear(source=self, for_value=output, generate_metadata=True)
            
            for column_index, column_metadata in enumerate(self._target_columns_metadata):
                output.metadata = output.metadata.update_column(column_index, column_metadata, source=self)

            return CallResult(output)
        else:
            raise ValueError('Model should be fitted first.')


    def get_params(self)  -> Params:
        if not self._fitted:
            raise ValueError("Fit not performed.")
        return Params(strategy_ = self._strategy,
                      origin_inputs_ = self._origin_inputs,
                      origin_outputs_ = self._origin_outputs,
                      train_data_ = self._training_inputs,
                      train_label_ = self._training_outputs,
                      target_columns_metadata_ = self._target_columns_metadata,
                      structure_ = self._structure,
                      structure_fit_ = self._structure_fit,
                      dimension_ = self._dimension,
                      method_ = self._method,
                      residual_ = self._residual
        )


    def set_params(self, *, params: Params) -> None:
        self._fitted = True
        self._strategy = params['strategy_']
        self._method= params['method_']
        self._origin_inputs = params['origin_inputs_']
        self._origin_outputs = params['origin_outputs_']
        self._training_inputs = params['train_data_']
        self._training_outputs = params['train_label_']
        self._target_columns_metadata = params['target_columns_metadata_']
        self._structure_fit = params['structure_fit_']
        self._structure = params['structure_']
        self._dimension = params['dimension_']
        self._residual = params['residual_']
