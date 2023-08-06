# rpi_d3m_primitives_part2

The rpi_d3m_primitives_part2 python package contains the primitives developed for the DARPA d3m project by the Rensselaer Polytechnic Institute TA1 team. This repo helps install rpi_d3m_primitives_part2 package. It is a extension of the original package "rpi_d3m_primitives". Both the packages can be download and installed through pypi. [rpi_d3m_primitives](https://pypi.org/project/rpi-d3m-primitives). [rpi_d3m_primitives_part2](https://pypi.org/project/rpi-d3m-primitives-part2). The rpi_d3m_primitives_part2 package includes global causal discovery primitive. The installation of rpi_d3m_primitives_part2 requires pre-installation of jdk 8.

# RPI ta1 primitives:
## `rpi-d3m-primitives` Package:
* STMB feature selection primitive 
* S2TMB feature selection primitive 
* JMI feature selection primitive 
* TAN classification primitive 
## `rpi-d3m-primitives-part2` Package
* Discrete Global Causal Discovery primitive  `d3m.primitives.classification.global_causal_discovery.ClassifierRPI`
* Continuous Global Causal Discovery primitive  `d3m.primitives.regression.global_causal_discovery.RegressorRPI`

# Requirement:
* JDK 8 recommend openjdk-8-jdk-headless
* javabridge == 1.0.19
```sh
pip install javabridge==1.0.19
```
* numpy
* pandas
* pydot
* py-causal [CDC py-causal](https://github.com/bd2kccd/py-causal) 
```sh
pip install git+https://github.com/bd2kccd/py-causal.git@6201db7d21aa453a8b66bf632db930417209a430#egg=pycausal
```
* pgmpy==0.1.11
* graphviz
* lingam 

# Installation:
* rpi_d3m_primitives
```sh
pip install rpi-d3m-primitives
```
* rpi_d3m_primitives_part2
```sh
pip install -e git+https://gitlab.com/N.Yin/rpi-d3m-part2.git@eae74f62f47d3eaf306edf11d97a10c3ab62ad24#egg=rpi_d3m_primitives_part2
```
