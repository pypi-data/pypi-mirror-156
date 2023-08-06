"""
import numpy as np
import math
from sympy import *
from cmath import *
##############################
from scipy.stats import *
from sympy.stats import *
##################################
from itertools import *
from more_itertools import *
from scipy.special import *
from fractions import Fraction
import random
##############################################
import locale as loc
from IPython.display import display, Math, Latex
loc.setlocale(loc.LC_ALL, 'ru')
init_printing(use_unicode=True,use_latex=True)
from scipy.stats import *
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt, patches
from matplotlib.patches import Rectangle
import matplotlib.ticker as ticker
from matplotlib import rcParams
#########################
import locale
locale.setlocale(locale.LC_NUMERIC, 'russian')
plt.rcParams['axes.formatter.use_locale'] = True
#########
plt.rcParams["lines.linewidth"] = 3.5
#########
plt.rcParams['font.size'] = 36
plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams['mathtext.fontset'] = 'cm'
###################
from sympy.combinatorics import *
from sympy.interactive import init_printing
init_printing(perm_cyclic=False, pretty_print=True)
############################################
import seaborn as sns
import pandas as pd
##########################################
#from matplotlib.backends.backend_pdf import PdfPages
#########################################################
from statsmodels.distributions.empirical_distribution import ECDF
###########################################################
from functools import reduce
#################################
from sympy.ntheory.generate import Sieve, primerange

from scipy import integrate
import scipy.optimize as opt

import pandas as pd


df = pd.read_csv('ds6.4.10.csv', header=None, decimal=',', sep=';',encoding='cp1251') #, encoding='cp1251'
data=df
A, B, C, N ,Pi, theta_1, theta_2 = symbols('A B C N pi theta_1 theta_2')
lnL = -N*ln(2*Pi) - N * ln(theta_1**2) - N/2*ln(1-theta_2**2) - N/(2*theta_1**2*(1-theta_2**2))*((A)+(B)-2*theta_2*(C))
lnL
##

##
x = np.array(data[0])
y = np.array(data[1])
mu1=3
mu2=4
n=len(x)
##

##
np.mean((x-mu1)*(y-mu2))*2
##
##
lnL.subs([(N,n),(A,np.mean((x-mu1)**2)),(B,np.mean((y-mu2)**2)),(C,np.mean((x-mu1)*(y-mu2)))])
##
##
dt1 = simplify(diff(lnL,theta_1))
dt2 = simplify(diff(lnL,theta_2))
dt2
##
##
sol=solve([dt1,dt2],[theta_1,theta_2])
sol
##
##
hatTheta_1=simplify(sol[1][0])
hatTheta_1
##
##
hatTheta_2=simplify(sol[1][1])
hatTheta_2
##
##
hatTheta_1.subs([(A,np.mean((x-mu1)**2)),(B,np.mean((y-mu2)**2)),(C,np.mean((x-mu1)*(y-mu2)))]).evalf()
##
##
hatTheta_2.subs([(A,np.mean((x-mu1)**2)),(B,np.mean((y-mu2)**2)),(C,np.mean((x-mu1)*(y-mu2)))]).evalf()
##

"""