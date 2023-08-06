from setuptools import setup, find_packages
import os
from setuptools.command.develop import develop


setup(
	name='rpi_d3m_primitives_part2',  
	version='0.0.5',  
	author='Naiyu Yin, Zijun Cui, Yuru Wang, Qiang Ji',
	author_email='yinn2@rpi.edu',
	url='https://gitlab.com/N.Yin/rpi-d3m-part2.git',
	description='Partial RPI primitives for D3M. Including structured classifier and global causal discovery.',
	platforms=['Linux', 'MacOS'],
        keywords = 'd3m_primitive',
	classifiers=[
        'License :: OSI Approved :: MIT License',
    	'Operating System :: OS Independent',
    	'Programming Language :: Python'
	],
	entry_points = {
		'd3m.primitives': [
            'classification.global_causal_discovery.ClassifierRPI = rpi_d3m_primitives_part2.GCD_Classification:GCD_Classification',
            'regression.global_causal_discovery.RegressorRPI = rpi_d3m_primitives_part2.CBN_Regression:CBN_Regression',
            # 'classification.structured.BayesianRPI = rpi_d3m_primitives_part2.Bayesian_Classification:Bayesian_Classification'
			],
	},
	install_requires=[
		'd3m', 
		'javabridge==1.0.19',
		'pgmpy==0.1.11', 
		'pydot',
		'networkx', 
		'graphviz',
		'numpy', 
		'scipy', 
		'pandas', 
		'torch', 
		'pyparsing', 
		'statsmodels', 
		'tqdm', 
		'joblib',
		'lingam',
                'pycausal @ git+https://github.com/bd2kccd/py-causal.git@6201db7d21aa453a8b66bf632db930417209a430#egg=pycausal',
	],
	packages=find_packages()
)
