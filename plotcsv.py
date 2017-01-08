# -*- coding: utf-8 -*-
"""
Created on Sun Jan 08 16:40:09 2017

@author: Christian
"""

import numpy as np
import matplotlib.pyplot as plt

data = np.genfromtxt('c:/temp/sample.csv', delimiter=',', names=['t', 'v'])

plt.plot(data["t"], data["v"], c='r', label='the data')
plt.show()