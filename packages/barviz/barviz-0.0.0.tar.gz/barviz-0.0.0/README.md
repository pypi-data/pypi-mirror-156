# BarViz

A simple python module to visualize barycentric data.

## 1/ About

**barviz** is a minimalist python module, built on top of **plotly**, allowing to display data in a barycentric space. 

## 1/ Installation

To install barviz :
```
pip install --upgrade barviz
```
Ideally, barviz is designed to be used from a **Jupyter lab** notebook.\
 To create a complete virtual environment :
```
python -m venv barviz-env
source barviz-env/bin/activate
pip install --upgrade barviz jupyterlab
jupyter lab
```

## 2/ Using it

For the impatients :
```
from barviz import Simplex

my_simplex = Simplex.build(5)
my_simlex.plot()
```

## 3/ Documentation 

**User manual** is available in **[html format](https://pjluc.gricad-pages.univ-grenoble-alpes.fr/barviz-mod/user-manual.html)** and as a [Jupyter lab notebook](https://gricad-gitlab.univ-grenoble-alpes.fr/pjluc/barviz-mod/-/raw/main/docs/user-manual.ipynb?inline=false). 

Reference API : In progres... - Hum, it will be necessary to wait a little more ;-)
